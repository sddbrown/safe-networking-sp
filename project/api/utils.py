from elasticsearch import TransportError, RequestError, ElasticsearchException
#from utility.utils import searchDomains


def searchDomain():
    apiKey = app.config["AUTOFOCUS_API_KEY"]
    # First thing is to set the processed flag to 17 on the sfn-dns-event doc
    # meaning we at least try it (try except block with logging)

    # Second check to see if we already have the domain in sfn-dns-domains index
    #  If we do, set variable index-local var to 1.
    #   Next check the age of the index and see if it needs updating and set index-local
    #   variable to 3 so it will update it.
    #  Else we do not have it locally and will need to call AF for it.
    #   create the index for the domain name 
    #   set variable index-local to 3 so it can go to AF and update
    #  If variable index-local is set to 3 go to AF and update the index for 
    #    that domain and set variable index-local to 1
    # 
    # If index-local is 1 (it better be) then reference the sfn-dns-domains doc ID
    #   in the sfn-dns-event doc so that we can later look up the pertinatent data
    #   and tags for that domain against that event.  
    #  
    #  PRAY
    #
    #  
    # 
    
def processDNS(es,app):
    '''
    This funciton is used to add AutoFocus information to the unprocessed 
    entries in ElasticSearch.  
    '''
    qSize = app.config["DNS_INIT_QUERY_SIZE"]
    

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
                                .format(docs['hits']['total'],"sfn-dns-event"))


        priDocIds = dict()
        secDocIds = dict()
        count = 0
        for entry in docs['hits']['hits']:
            docKey = entry['_id']
            if entry['_source']['threat_name'] == "generic":
                secDocIds[docKey] = entry['_source']['domain_name']
            else:
                priDocIds[docKey] = entry['_source']['domain_name']
                print(f"{docKey} : {priDocIds[docKey]} - {entry['_source']['threat_name']}")
                count += 1
        #searchDomains('xiterzao.ddns.net',apiKey)
        print(count)    
    except TransportError:
        app.logger.warning('Initialization was unable to find the index sfn-dns-event')
    


def main():
    pass

if __name__ == "__main__":
    main()
    