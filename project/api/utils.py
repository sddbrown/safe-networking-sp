from elasticsearch import TransportError


def processDNS(es,app):

    qSize = app.config["DNS_INIT_QUERY_SIZE"]

    try:
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

        #docList = {doc['_id']:doc['threat_id'] for doc in docs['hits']['hits']}
        docIds = dict()
        for entry in docs['hits']['hits']:
            docKey = entry['_id']
            print(docKey)
            docIds[docKey] = entry['_source']['threat_id']
            print("{0} : {1}".format(docKey,docIds[docKey]))
            
    except TransportError:
        app.logger.warning('Initialization was unable to find the index sfn-dns')
    
#     return docIds

# # Initiate
# docIds = startProcessing()
# pprint.pformat(json.dumps(docIds))
# app.logger.debug("Found {0}".format(docIds))

def main():
    pass

if __name__ == "main":
    main()
    