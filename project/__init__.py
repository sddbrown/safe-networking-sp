# project/__init__.py

import os
import logging
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_elasticsearch import Elasticsearch
from logging.handlers import RotatingFileHandler
#from elasticsearch import Elasticsearch, ElasticsearchException
#from flask.ext.elasticsearch import FlaskElasticsearch


# Initialize the app for Flask
app = Flask(__name__)


# Set the configuration parameters that are used by the application.  
# These values are overriden by the .panrc file located in the base directory
# for the application
#
# ---------- APPLICATION SETTINGS --------------
#
# Current version number of SafeNetworking
app.config['VERSION'] = "0.1-dev"
#
# The debug setting for Flask.  Shows messages on *console* 
app.config['DEBUG'] = False
#
# Flask setting for where session manager contains the info on the session(s)
app.config['SESSION_TYPE'] = "filesystem"
#
# Secret key needed by session setting above.  
app.config['SECRET_KEY'] = "\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5"
#
# Sets the base directory for the application
app.config['BASE_DIR'] = os.path.abspath(os.path.dirname(__file__)) 
#
# Set the number of seconds for multi-threading to wait between processing calls
# of any events deemed as "primary" 
app.config['POOL_TIME'] = 60   
#
# Set the number of seconds - what the hell is this for?
#app.config['SEC_PROCESS_POOL_TIME'] = 300
#
# When SafeNetworking is started, number of documents to read from the DB.  The
# larger the number, the longer this will take to catch up.  
app.config['DNS_INIT_QUERY_SIZE'] = 200
app.config['IOT_INIT_QUERY_SIZE'] = 1000
# app.config['SEC_PROCESS_QUERY_SIZE'] = 1000 - what the hell is this for?
#
# SafeNetworking caches domain info from AutoFocus.  This setting specifies, in 
# days, how long the cache is ok.  If there is cached info on this domain and it
# is older than the setting, SFN will query AF and update as necessary and reset
# the cache "last_updated" setting in ElasticSearch.
app.config['DNS_DOMAIN_INFO_MAX_AGE'] = 30
#
# The Autofocus API isn't the speediest thing on the planet.  Usually, the most 
# pertinent info is within the first couple of minutes of query time.  So, set
# this to drop out of the processing loop and stop waiting for the query to 
# finish - which could take 20mins.  No lie....   This is set in minutes
app.config['AF_LOOKUP_TIMEOUT'] = 1
#
# The maximum percentage of the AF query we are willing to accept.  If, when we
# check the timer above, the value is greater than this percentage, we bail out
# of the loop.  The lower the number, the more likely that we may not get a 
# result.  Though, usually, 1 minute and 50 percent is enough to get at least 
# the latest result.
app.config['AF_LOOKUP_MAX_PERCENTAGE'] = 50
#
# The maximum age for tag info.  This doesn't need to be updated as often as 
# the domain or other items, but should be done periodically just in case.. 
# Setting is in days.
app.config['AF_TAG_INFO_MAX_AGE'] = 120
#
#
# ------------------------------- LOGGING --------------------------------------
#
# Log level for the SafeNetworking application itself.  All files are written
# to log/sfn.log
app.config['LOG_LEVEL'] = "WARNING"
#
# Size of Log file before rotating - in bytes
app.config['LOG_SIZE'] = "10000000"
#
# Number of log files to keep in log rotation
app.config['LOG_BACKUPS'] = "10"
#
#
#
# ----------------------------- ELASTICSTACK -----------------------------------
#
# By default our ElasticStack is installed all on the same system
app.config['ELASTICSEARCH_HOST'] = "localhost"
app.config['ELASTICSEARCH_PORT'] = "9200"
app.config['ELASTICSEARCH_HTTP_AUTH'] = ""
app.config['KIBANA_HOST'] = "localhost"
app.config['KIBANA_PORT'] = "5601"
app.config['ELASTICSTACK_VERSION'] = "6.1.1"
#
#
#
# ----------------------------- MISCELLANEOUS ----------------------------------
#
app.config['AUTOFOCUS_HOSTNAME'] = "autofocus.paloaltonetworks.com"
app.config['AUTOFOCUS_SEARCH_URL'] = "https://autofocus.paloaltonetworks.com/api/v1.0/samples/search"
app.config['AUTOFOCUS_RESULTS_URL'] = "https://autofocus.paloaltonetworks.com/api/v1.0/samples/results/"
#
#

# Set instance config parameters
app.config.from_pyfile('.panrc')
# Add bootstrap object for Flask served pages
bs = Bootstrap(app)
# Add Elasticsearch object for our instance of ES 
es = Elasticsearch(f"{app.config['ELASTICSEARCH_HOST']}:{app.config['ELASTICSEARCH_PORT']}")

# Set up logging for the application - we may want to revisit this 
# see issue #10 in repo
handler = RotatingFileHandler('log/sfn.log', 
                            maxBytes=10000000, 
                            backupCount=10)
logFormat = logging.Formatter('%(asctime)s - %(funcName)s<%(lineno)i> - [%(levelname)s] : %(message)s')
handler.setLevel(app.config["LOG_LEVEL"])
handler.setFormatter(logFormat)
app.logger.addHandler(handler)
app.logger.info(f"INIT - SafeNetworking application initializing with log level of {app.config['LOG_LEVEL']}")
app.logger.info(f"ElasticSearch host is: {app.config['ELASTICSEARCH_HOST']}:{app.config['ELASTICSEARCH_PORT']}")

# Register blueprints
from project.api.views import sfn_blueprint
app.register_blueprint(sfn_blueprint)



    
# def create_app():
#     '''
#     - Configuration settings come from the main level .panrc file
#         and are superseded by project/instance/.panrc file.
#     - Create logging handler for application
#     - Sets up threading in background to take care of talking to external data
#         systems to add to documents in ElasticSearch
#     - Registers all blueprints within the app itself
#     - Finally, returns the SafeNetworking application.
#     '''

#     # Instantiate the app
#     app = Flask(__name__)
#     ctx = app.app_context()
#     #ctx.push()
    
#     with ctx:
        
#         # Set config parameters
#         app.config.from_pyfile('.panrc')
#         app.config.from_pyfile('instance/.panrc')
        
#         # Set up logging for the application - we may want to revisit this 
#         # see issue #10 in repo
    
#         handler = RotatingFileHandler('log/sfn.log', 
#                                     maxBytes=10000000, 
#                                     backupCount=10)
#         logFormat = logging.Formatter('%(asctime)s - %(funcName)s<%(lineno)i> - [%(levelname)s] : %(message)s')
#         handler.setLevel(app.config["LOG_LEVEL"])
#         handler.setFormatter(logFormat)
#         app.logger.addHandler(handler)
#         app.logger.info("\n-------------------------------------------------------------------------------------------\n")
#         app.logger.info(f"INIT - SafeNetworking application initializing with log level of {app.config['LOG_LEVEL']}")

#         # Register blueprints
#         from project.api.views import sfn_blueprint
#         app.register_blueprint(sfn_blueprint)

#         return app
