from flask import Blueprint, jsonify, request, render_template, current_app
from flask import flash



sfn_blueprint = Blueprint('sfn', __name__, template_folder='./templates')
@sfn_blueprint.route('/')
def index():
    return render_template('searchbase.html')

@sfn_blueprint.route('/login')
def login():
    #form = LoginForm()
    return render_template('index.html', form=form)

@sfn_blueprint.route('/dashboard')
def dashboard():
    # Create the URL for Kibana using the config options set at runtime
    KIBANA_URL = "{0}:{1}".format(current_app.config["KIBANA_HOST"],
                                  current_app.config["KIBANA_PORT"])
    return render_template('dashboard.html',kibana_host=KIBANA_URL)

@sfn_blueprint.route('/domains')
def domains():
    KIBANA_URL = "{0}:{1}".format(current_app.config["KIBANA_HOST"],
                                  current_app.config["KIBANA_PORT"])
    return render_template('domains.html', kibana_host=KIBANA_URL)

@sfn_blueprint.route('/iot')
def iot():
    KIBANA_URL = "{0}:{1}".format(current_app.config["KIBANA_HOST"],
                                  current_app.config["KIBANA_PORT"])
    return render_template('iot.html', kibana_host=KIBANA_URL)
