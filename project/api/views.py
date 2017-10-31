from flask import Blueprint, jsonify, request, render_template, current_app
#from models import Member
#from forms import LoginForm
#from flask import render_template

sfn_blueprint = Blueprint('sfn', __name__, template_folder='./templates')
@sfn_blueprint.route('/')
def index():
    return render_template('index.html')

@sfn_blueprint.route('/login')
def login():
    #form = LoginForm()
    return render_template('index.html', form=form)

@sfn_blueprint.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', KIBANA_HOST=current_app.config["KIBANA_HOST"])

@sfn_blueprint.route('/domains')
def domains():
    return render_template('domains.html')

@sfn_blueprint.route('/iot')
def iot():
    return render_template('iot.html')
