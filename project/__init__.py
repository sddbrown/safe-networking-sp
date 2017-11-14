# project/__init__.py

import os
import datetime
import threading
import atexit
from flask import Flask, jsonify
from pprint import pprint as pp



def create_app():
    ''' 
    Returns the SafeNetworking application.
    Configuration settings come from the main level config.py file
    and are superseded by project/instance/config.py file. 
    Registers all blueprints within the app itself 
    '''

    # instantiate the app
    app = Flask(__name__)
    
    # set config parameters
    app.config.from_pyfile('config')
    app.config.from_pyfile('instance/sfn.cfg')

    pp(app.config)
    

    # set up extensions
    # db.init_app(app)

    # register blueprints
    from project.api.views import sfn_blueprint
    app.register_blueprint(sfn_blueprint)

    return app
