from elasticsearch import TransportError, RequestError, ElasticsearchException
from utility.utils import searchDomains


def processDNS(es,app):
    '''
    This funciton is used to add AutoFocus information to the unprocessed 
    entries in ElasticSearch.  
    '''
    qSize = app.config["DNS_INIT_QUERY_SIZE"]
    apiKey = app.config["AUTOFOCUS_API_KEY"]

    try:
        # Query for the unprocessed DNS entries.  
        docs = es.search(index="sfn-dns-event",
                         body={
                            "size": qSize, 
                            "sort": [{"msg_gen_time": {"order": "desc"}}], 
                            "query": { 
                                "bool": { 
                                "must": [
                                    {"match": {"threat_category": "wildfire"}}, 
                                    {"match": {"processed": "0"}}] # end must
                                }  # end bool
                            }
                          }   # end body
                        )

        app.logger.info("Found {0} unpropcessed document(s) for {1}"
                                .format(docs['hits']['total'],"sfn-dns"))

        # Create a dictionary of the docs and the associate threat_id
       # docIds = {doc['_id']:doc['_source']['threat_id'] for doc in }
        #print(dict(docIds))
        
        # Need to manipulate the threat_id to break out the domain - would be
        # better to do this with the logger - need to figure that out.
        # docIds = dict()
        # for entry in docs['hits']['hits']:
        #     docKey = entry['_id']
        #     docIds[docKey] = entry['_source']['domain_name']
        #     #print("{0} : {1}".format(docKey,docIds[docKey]))
        searchDomains('xiterzao.ddns.net',apiKey)
            
    except TransportError:
        app.logger.warning('Initialization was unable to find the index sfn-dns')
    


def main():
    pass

if __name__ == "__main__":
    main()
    