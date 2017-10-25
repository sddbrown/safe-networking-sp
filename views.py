from myapp import app
#from models import Member
from forms import LoginForm
from flask import render_template

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('index.html', form=form)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/domains')
def domains():
    return render_template('domains.html')

@app.route('/iot')
def iot():
    return render_template('iot.html')
