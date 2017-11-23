from elasticsearch import TransportError


def processDNS(es,app):
    '''
    This funciton is used to add AutoFocus information to the unprocessed 
    entries in ElasticSearch.  
    '''
    qSize = app.config["DNS_INIT_QUERY_SIZE"]

    try:
        # Query for the unprocessed DNS entries.  
        docs = es.search(index="sfn-dns",
                         body={"size": qSize, 
                               "query": { 
                                  "bool": { 
                                    "must": [
                                      {"match": {"threat_category": "wildfire"}}, 
                                      {"match": {"processed": "0"}}
                                    ]
                                  }
                                }
                              }
                        )

        app.logger.info("Found {0} unpropcessed document(s) for {1}"
                                .format(docs['hits']['total'],"sfn-dns"))

        # Create a dictionary of the docs and the associate threat_id
       # docIds = {doc['_id']:doc['_source']['threat_id'] for doc in }
        #print(dict(docIds))
        
        # Need to manipulate the threat_id to break out the domain - would be
        # better to do this with the logger - need to figure that out.
        docIds = dict()
        for entry in docs['hits']['hits']:
            docKey = entry['_id']
            docIds[docKey] = entry['_source']['threat_id']
            print("{0} : {1}".format(docKey,docIds[docKey]))
            
    except TransportError:
        app.logger.warning('Initialization was unable to find the index sfn-dns')
    


def main():
    pass

if __name__ == "main":
    main()
    