# project/__init__.py

import os
import datetime
from flask import Flask, jsonify
#from flask_sqlalchemy import SQLAlchemy


def create_app():
    ''' 
    Returns the SafeNetworking application.
    Configuration settings come from the project/instance/config.py file. 
    Registers all blueprints within the app itself 
    '''

    # instantiate the app
    app = Flask(__name__)
    
    # set config
    app.config.from_pyfile('instance/config.py')


    # set up extensions
    # db.init_app(app)

    # register blueprints
    from project.api.views import sfn_blueprint
    app.register_blueprint(sfn_blueprint)

    return app
