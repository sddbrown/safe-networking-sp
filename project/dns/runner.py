import time
import datetime
from project import app
from elasticsearch_dsl import Search
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
from project.dns.dns import DNSEventDoc
from elasticsearch import TransportError
from elasticsearch_dsl import connections
from elasticsearch.exceptions import NotFoundError
from project.dns.dnsutils import getDomainDoc, assessTags




def processDNS():
    '''
    This function is used to gather the unprocessed docs in ElasticSearch and 
    put them into one of two lists - primary (named threats) or secondary 
    ("generic") threats.  It will process the latest document up to the maximum 
    defined number of documents (DNS_INIT_QUERY_SIZE).  The primary threats will
    be processed in real-time using multiprocessing.  The generic threats will be
    processed after the primary threats are done.
    '''
    now = datetime.datetime.now()
    priDocIds = dict()
    secDocIds = dict()
    qSize = app.config["DNS_EVENT_QUERY_SIZE"]
    timeLimit = (now - datetime.timedelta(days=app.config['DNS_DOMAIN_INFO_MAX_AGE']))
    updateDetails = False
    
    app.logger.debug(f"Gathering {qSize} sfn-dns-events from ElasticSearch")

    # Define the default Elasticsearch client
    connections.create_connection(hosts=[app.config['ELASTICSEARCH_HOST']])

    # Create search for all unprocessed events
    eventSearch = Search(index="sfn-dns-event") \
                .query("match", threat_category="wildfire") \
                .query("match", processed=0)  \
                .sort({"received_at": {"order" : "asc"}})

    # Limit the size of the returned docs to the specified config paramter
    eventSearch = eventSearch[:qSize]

    # Execute the search
    searchResponse =  eventSearch.execute()
   
    # For each hit, classify the event as either primary (we have the domain
    # info cached) or secondary (need to look it up) and add the event ID to the
    # appropriate dictionary as the key and the domain
    # name as the value associated with it
    for hit in searchResponse.hits:

        # Check to see if we have a domain doc for it already.  If we do, 
        # add it to be processed first, if not, add it to the AF lookup
        # queue (secDocIds)
        domainSearch = Search(index="sfn-domain-details") \
                        .query("match", name=hit.domain_name)
        if domainSearch.execute():
            priDocIds[hit.meta.id] = hit.domain_name
            app.logger.debug(f"{hit.meta.id} : {priDocIds[hit.meta.id]} - " +
                             f"{hit.threat_name}")

        else:
            secDocIds[hit.meta.id] = hit.domain_name
            app.logger.debug(f"{hit.meta.id} : {secDocIds[hit.meta.id]} - " +
                             f"{hit.threat_name}")
        
            
    app.logger.debug(f"priDocIds are {priDocIds}")
    app.logger.debug(f"secDocIds are {secDocIds}")


    # If we aren't in DEBUG mode (.panrc setting)
    if not app.config['DEBUG_MODE']:
        '''
        pool.map will take any iterable but it changes it to a list,
        so in our case, the keys get pulled and sent as a list.  This is a 
        bummer because the searchDomain is going to have to do the same 
        lookup (that we just fricken did) to find the domain name.  Need to
        find a better way to do this to prevent more lookups.  
        '''
        # Multiprocess the primary keys
        with Pool(cpu_count() * 4) as pool:
            results = pool.map(searchDomain, priDocIds)
        
        app.logger.debug(f"Results for processing primary events {results}")
        
        # Do the same with the generic/secondary keys and pace so we don't kill AF
        with Pool(cpu_count() * 4) as pool:
            results = pool.map(searchDomain, secDocIds)
        
        app.logger.debug(f"Results for processing AF lookup events {results}")

    # This else gets triggered so we only do one document at a time and is for 
    # debugging at a pace that doesn't overload the logs. Load the secondary
    # docs as well, in case we run out of primary while debugging
    else:
        for document in priDocIds:
            try:
                searchDomain(document)
            except Exception as e:
                app.logger.error(f"Exception recieved processing document " +
                                 f"{document}: {e}")
        for document in secDocIds:
            try:
                searchDomain(document)
            except Exception as e:
                app.logger.error(f"Exception recieved processing document " +
                                 f"{document}: {e}")

        

def searchDomain(eventID):       
    '''
    Receives the ID of the event doc and gets the domain to search for 
    from that doc.  Calls getDomainDoc() and looks at the known tags
    for the domain (if they exist).  Then calls assessTags() to determine
    the most probable campaign/actor/malware for the given set of tags.
    Writes that info to the event doc and updates it using the class save()
    method.
    '''
    processedValue = 0

    try:
        eventDoc = DNSEventDoc.get(id=eventID)
        domainName = eventDoc.domain_name
        domainDoc = getDomainDoc(domainName)


        if "NULL" in domainDoc:
            app.logger.warning(f"Unable to process event {eventID} beacause" +
                               f" of problem with domain doc {domainName}")
        else:
            app.logger.debug(f"Assessing tags for domain-doc {domainDoc.name}")

            #  Set dummy info if no tags were found
            if "2000-01-01T00:00:00" in str(domainDoc.tags):
                eventTag = {'tag_name': 'No tags found for domain', 
                            'public_tag_name': 'No tags found for domain',
                            'tag_class': 'No tags found for domain',
                            'sample_date': '2000-01-01T00:00:00',
                            'file_type': 'NA',
                            'confidence_level': 0}
                processedValue = 55
            else: 
                eventTag = assessTags(domainDoc.tags)
                processedValue = 1
            
            try:
                eventDoc.event_tag = eventTag
                eventDoc.updated_at = datetime.datetime.now()
                eventDoc.processed = processedValue
                eventDoc.save()
                app.logger.debug(f"Saved event doc with the following data:" +
                                f" {eventDoc}")
                return (f"{eventID} save: SUCCESS")
            except TransportError as te:
                app.logger.error(f"Transport Error working with {eventID}:" +
                                f" {te.info} ")
                return (f"{eventID} save: FAIL")
            except Exception as e:
                app.logger.error(f"Unable to work with event doc {eventID} - {e}")
                return (f"{eventID} save: FAIL")
   
    except Exception as e:
                app.logger.error(f"Unable to work with event doc {eventID} - {e}")
                return (f"{eventID} save: FAIL")
        


def main():
    processDNS()



if __name__ == "__main__":
    main()