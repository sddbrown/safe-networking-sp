



docIds = {}
    #     indexes = ("sfn-dns","sfn-iot")
    #     qSize = app.config["INIT_QUERY_SIZE"]

    #     try:
    #         for index in indexes:
    #             # Search for all docs that have processed set to 0, which means they 
    #             # have not been processed yet.
    #             docs = es.search(index=index,body={
    #                                                 "size": qSize, 
    #                                                 "query": {
    #                                                     "match_all": {}
    #                                                 },
    #                                                 "sort": [
    #                                                     {
    #                                                     "msg_gen_time": {
    #                                                         "order": "desc"
    #                                                     }
    #                                                     }
    #                                                 ]
    #                                             }
    #             )
    #             app.logger.info(
    #                         "Found {0} unpropcessed document(s) for {1}"
    #                                     .format(docs['hits']['total'],index))

    #             for doc in docs['hits']['hits']:
    #                 docKey = doc['_id']
    #                 print("{0}".format(docKey))
    #                 docIds[docKey] = index
                
                
    #     except TransportError:
    #         app.logger.warning('Initialization was unable to find the index {0}'.format(index))
        
    #     return docIds

    # # Initiate
    # docIds = startProcessing()
    # pprint.pformat(json.dumps(docIds))
    # app.logger.debug("Found {0}".format(docIds))

if __name__ == "main":
    