# project/__init__.py

import logging
from flask import Flask

from logging.handlers import RotatingFileHandler
#from flask.ext.elasticsearch import FlaskElasticsearch


    
def create_app():
    '''
    - Configuration settings come from the main level .panrc file
        and are superseded by project/instance/.panrc file.
    - Create logging handler for application
    - Sets up threading in background to take care of talking to external data
        systems to add to documents in ElasticSearch
    - Registers all blueprints within the app itself
    - Finally, returns the SafeNetworking application.
    '''

    # Instantiate the app
    app = Flask(__name__)
    ctx = app.app_context()
    #ctx.push()
    
    with ctx:
        
        # Set config parameters
        app.config.from_pyfile('.panrc')
        app.config.from_pyfile('instance/.panrc')
        
        # Set up logging for the application - we may want to revisit this 
        # see issue #10 in repo
    
        handler = RotatingFileHandler('log/sfn.log', 
                                    maxBytes=10000000, 
                                    backupCount=10)
        logFormat = logging.Formatter('%(asctime)s - %(funcName)s<%(lineno)i> - [%(levelname)s] : %(message)s')
        handler.setLevel(app.config["LOG_LEVEL"])
        handler.setFormatter(logFormat)
        app.logger.addHandler(handler)
        app.logger.info("\n-------------------------------------------------------------------------------------------\n")
        app.logger.info(f"INIT - SafeNetworking application initializing with log level of {app.config['LOG_LEVEL']}")

        # Register blueprints
        from project.api.views import sfn_blueprint
        app.register_blueprint(sfn_blueprint)

        return app
