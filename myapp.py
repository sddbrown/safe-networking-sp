from flask import Flask
from flask_elasticsearch import FlaskElasticsearch

app = Flask(__name__)

app.config.from_pyfile('config.py')

db = FlaskElasticsearch(app)


from views import *

if __name__ == '__main__':
    app.run()
