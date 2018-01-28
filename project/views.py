from flask import Blueprint, jsonify, request, render_template, current_app
from flask import flash



sfn_blueprint = Blueprint('sfn', __name__, template_folder='./templates')
@sfn_blueprint.route('/')
def index():
    return render_template('index.html')