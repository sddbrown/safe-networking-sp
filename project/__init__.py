# project/__init__.py

import os
import datetime
from flask import Flask, jsonify
#from flask_sqlalchemy import SQLAlchemy


# instantiate the app
#app = Flask(__name__)

# set config
#app_settings = os.getenv('APP_SETTINGS')
#app.config.from_object('project.config.DevelopmentConfig')


def create_app():

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
