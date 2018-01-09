import sys
import json
import time
import datetime
import requests
from pprint import pprint as pp
from random import randint
from project import app, es
from project.api.dns.dnsutils import getDomainInfo
from project.api.dns.dns import DomainDetailsDoc, DNSEventDoc
from project.api.utils import *
from collections import OrderedDict
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
from elasticsearch import TransportError, RequestError, ElasticsearchException
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import DocType, Search, Date, Integer, Keyword, Text, Ip, connections





def processDNS():
    '''
    This function is used to gather the unprocessed docs in ElasticSearch and 
    put them into one of two lists - primary (named threats) or secondary 
    ("generic" threats.  It will process the latest document up to the maximum 
    defined number of documents (DNS_INIT_QUERY_SIZE).  The primary threats will
    be processed in real-time using multiprocessing.  The secondaries will have
    their "processed" value changed to 55.  This value is searched on by the
    process  
    '''
    now = datetime.datetime.now()
    qSize = app.config["DNS_EVENT_QUERY_SIZE"]
    timeLimit = (now - datetime.timedelta(days=app.config['DNS_DOMAIN_INFO_MAX_AGE']))
    updateDetails = False
    

    # Define a default Elasticsearch client
    connections.create_connection(hosts=[app.config['ELASTICSEARCH_HOST']])

    # Create search for all unprocessed events that are not generic
    eventSearch = Search(index="sfn-dns-event") \
                .query("match", threat_category="wildfire") \
                .query("match", processed=0)  \
                .sort({"received_at": {"order" : "asc"}}) \
                .exclude("term", threat_name="generic")

    # Limit the size of the returned docs to the specified config paramter
    eventSearch = eventSearch[:qSize]

    # Execute the search
    eventSearch.execute()

    for idx,hit in enumerate(eventSearch):
        print(idx, hit.threat_name, hit.domain_name)
    
        try:
            domainDoc = DomainDetailsDoc.get(id=hit.domain_name)

            # check age of doc and set to update the details
            #
            # updateDetails = True

        except NotFoundError as nfe:
            app.logger.info(f"Making new doc for domain {hit.domain_name}")
            updateDetails = True

        if updateDetails:
            afDomainData = getDomainInfo(hit.domain_name)
            domainDoc = DomainDetailsDoc(meta={'id': hit.domain_name}, name=hit.domain_name,
                                            tags=['test'])

            pp(json.dumps(afDomainData))
            domainDoc.tags = json.dumps(afDomainData)
            domainDoc.created_at = datetime.datetime.now().isoformat(' ')
            domainDoc.updated_at = datetime.datetime.now().isoformat(' ')
            domainDoc.type_of_doc = "domain-doc"
            domainDoc.save()
        
            app.logger.debug(domainDoc.body)
            
    exit()
    # qSize = app.config["DNS_INIT_QUERY_SIZE"]
    # priDocIds = dict()
    # secDocIds = dict()

    # app.logger.debug(f"Gathering {qSize} sfn-dns-events from ElasticSearch")

    # try:
    #     # Query for the unprocessed DNS entries.  
    #     docs = es.search(index="sfn-dns-event",
    #                      body={
    #                         "size": qSize, 
    #                         "sort": [{"@timestamp": {"order": "desc"}}], 
    #                         "query": { 
    #                             "bool": { 
    #                                 "must": [
    #                                     {"match": {"threat_category": "wildfire"}}, 
    #                                     {"match": {"processed": "0"}}]}}})
    # except Exception as e:
    #     app.logger.error(f"Unable to find the index sfn-dns-event: {e.info}")

    # app.logger.info(f"Found {docs['hits']['total']} unpropcessed documents " + 
    #                 f"for sfn-dns-event")


    # # Categorize the entries as either primary (has a threat name) or secondary
    # for entry in docs['hits']['hits']:
    #     docKey = entry['_id']
    #     if entry['_source']['threat_name'] == "generic":
    #         secDocIds[docKey] = entry['_source']['domain_name']
    #         app.logger.debug(f"{docKey} : {secDocIds[docKey]} - " +
    #                          f"{entry['_source']['threat_name']}")
    #     else:
    #         priDocIds[docKey] = entry['_source']['domain_name']
    #         app.logger.debug(f"{docKey} : {priDocIds[docKey]} - " +
    #                          f"{entry['_source']['threat_name']}")
                    
    # app.logger.info(f"Found {len(priDocIds)} known threats")
    # app.logger.info(f"Found {len(secDocIds)} 'generic' threats")

    # if not app.config['DEBUG_MODE']:
    #     '''
    #     rool.map will take any iterable but it changes it to a list,
    #     so in our case, the keys get pulled and sent as a list.  This is a 
    #     bummer because the searchDomain is going to have to do the same 
    #     lookup (that we just fricken did) to find the domain name.  Need to
    #     find a better way to do this to prevent more lookups.  
    #     '''
    #     # Multiprocess the primary keys
    #     with Pool(cpu_count() * 4) as pool:
    #         results = pool.map(searchDomain, priDocIds)
        
    #     app.logger.debug(results)
        
    #     # Do the same with the generic/secondary keys and pace so we don't kill AF
    #     with Pool(cpu_count() * 4) as pool:
    #         results = pool.map(searchDomain, secDocIds)
        
    #     app.logger.debug(results)

    # # This gets triggered so we only do one document at a time and is for 
    # # debugging at a pace that doesn't overload the logs. Load the secondary
    # # docs as well, in case we run out of primary while debugging
    # else:
    #     for document in priDocIds:
    #         try:
    #             searchDomain(document)
    #         except Exception as e:
    #             app.logger.error(f"Exception recieved processing document " +
    #                              f"{document}: {e}")
    #     for document in secDocIds:
    #         try:
    #             searchDomain(document)
    #         except Exception as e:
    #             app.logger.error(f"Exception recieved processing document " +
    #                              f"{document}: {e}")




def main():
    pass



if __name__ == "__main__":
    main()