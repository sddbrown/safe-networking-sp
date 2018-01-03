# import sys
# import json
# import time
import datetime
#import requests
from project import app
#from elasticsearch import TransportError, RequestError, ElasticsearchException


def calcCacheTimeout(cacheTimeout,lastDate,docID):
    '''
    Calculate the time difference between two formatted date strings
    '''
    now = datetime.datetime.now()
    lastUpdatedDate = datetime.datetime.strptime(lastDate, '%Y-%m-%dT%H:%M:%SZ')
    calcDate = abs((now - lastUpdatedDate).days) 

    if calcDate < cacheTimeout:
        app.logger.debug(f"Processing of {docID} is {calcDate} days vs setting"+ 
                         f" of {cacheTimeout} days and should be good")
        return True
    else:
        app.logger.debug(f"Processing of {docID} is {calcDate} days vs setting"+
                         f" of {cacheTimeout} and needs to be updated")
        return False




def main():
    pass

if __name__ == "__main__":
    main()
    