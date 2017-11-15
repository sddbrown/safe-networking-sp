# project/__init__.py

import os
import json
import datetime
import threading
import atexit
import logging
from flask import Flask, jsonify
from pprint import pprint as pp
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError
from logging.handlers import RotatingFileHandler


    
def create_app():
    '''
    - Configuration settings come from the main level config.py file
        and are superseded by project/instance/config.py file.
    - Create logging handler for application
    - Sets up threading in background to take care of talking to external data
        systems to add to documents in ElasticSearch
    - Registers all blueprints within the app itself
    - Finally, returns the SafeNetworking application.
    '''

    # Instantiate the app
    app = Flask(__name__)
    
    # Set config parameters
    app.config.from_pyfile('config')
    app.config.from_pyfile('instance/sfn.cfg')
    
    # Set up logging for the application - we may want to revisit this (see #10)
   
    handler = RotatingFileHandler('log/sfn.log', 
                                   maxBytes=10000, 
                                   backupCount=10)
    logFormat = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s] - %(message)s')
    handler.setLevel(app.config["LOG_LEVEL"])
    handler.setFormatter(logFormat)
    app.logger.addHandler(handler)
    app.logger.info("\n\n[INIT] SafeNetworking application initializing......\n")


    # Set up the ElasticSearch object for our instance of ES
    es = Elasticsearch([{'host': app.config["ELASTICSEARCH_HOST"],
                         'port': app.config["ELASTICSEARCH_PORT"]}])

    
    def startProcessing():
        '''
        Initializes the search list and sets the "processed" value to 17 so that
        the app knows that the document has been picked up for processing. It
        then calls the threading/multiprocessing function processDocuments() to
        continually search through ElasticSearch DB for unprocessed docs.
        '''
        # Set up variables used for processing
        docIds = {}
        indexes = ("sfn-dns","sfn-iot")

        try:
            for index in indexes:
                # Search for all docs that have processed set to 0, which means they 
                # have not been processed yet.
                docs = es.search(
                    index=index,
                    body={
                        "query": {
                            "match": {
                                "processed": "0"}}})

                app.logger.info(
                            "Found {0} unpropcessed document(s) for {1}"
                                        .format(docs['hits']['total'],index))

                for doc in docs['hits']['hits']:
                    docKey = doc['_id']
                    print("{0}".format(docKey))
                    docIds[docKey] = index
                
                app.logger.info("Found {0}".format(json.dumps(docIds)))
        except TransportError:
            app.logger.warning('Initialization was unable to find the index {0}'.format(index))

    # Initiate
    startProcessing()

    # When we kill Flask (SIGTERM), we want to clear the trigger for the
    # next thread
    # atexit.register(interrupt)

    # Register blueprints
    from project.api.views import sfn_blueprint
    app.register_blueprint(sfn_blueprint)

    return app
