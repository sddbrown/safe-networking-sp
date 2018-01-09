
import json
import time
import requests
import datetime
from project import app
from pprint import pprint as pp
from elasticsearch.exceptions import NotFoundError
from project.api.dns.dns import AFDetailsDoc, TagDetailsDoc
from elasticsearch_dsl import DocType, Search, Date, Integer, Keyword, Text, Ip, connections


def calcTimeDiff(eDate,sDate):
       
    if isinstance(eDate,str):
        app.logger.debug(f"Converting {eDate} to date object")
        eDate = datetime.datetime.strptime(eDate,'%Y-%m-%dT%H:%M:%SZ')

    if isinstance(sDate,str):
        app.logger.debug(f"Converting {sDate} to date object")
        sDate = datetime.datetime.strptime(sDate,'%Y-%m-%dT%H:%M:%SZ')

    app.logger.debug(f"Calculating time difference for {eDate} and {sDate}")
    
    return  abs((eDate - sDate).days)



def updateAfStats(afInfo):
    '''
    Update the sfn-details af-doc. 
    If it doesn't exist, the 'upsert' does that for us. 
    '''
    # Define a default Elasticsearch client
    #connections.create_connection(hosts=[app.config['ELASTICSEARCH_HOST']])
    

    try:
        afDoc = AFDetailsDoc.get(id='af-details')

    except NotFoundError as nfe:
        app.logger.info(f"The af-details doc is not found - creating")
           
        afDoc = AFDetailsDoc(meta={'id': 'af-details'}, 
                                    minute_points=0,
                                    minute_points_remaining=0,
                                    daily_points=0,
                                    daily_points_remaining=0,
                                    minute_bucket_start=now,
                                    daily_bucket_start=now)
    
    
    # The AF Doc should exist by now
    afDoc.minute_points=afInfo['minute_points']
    afDoc.minute_points_remaining=afInfo['minute_points_remaining']
    afDoc.daily_points=afInfo['daily_points']
    afDoc.daily_points_remaining=afInfo['daily_points_remaining']
    afDoc.minute_bucket_start=afInfo['minute_bucket_start']
    afDoc.daily_bucket_start=afInfo['daily_bucket_start']
    afDoc.save()



def getTagInfo(tagName):
    '''
    Method that uses user supplied api key (.panrc) and gets back the info on
    the tag specified as tagName.  This doesn't take very long so we don't have
    to do all the crap we did when getting domain info
    Calls:
        calcCacheTimeout()

    '''
    searchURL = app.config["AUTOFOCUS_TAG_URL"] + f"{tagName}"
    print(searchURL)
    headers = {"Content-Type": "application/json"}
    data = {"apiKey": app.config['AUTOFOCUS_API_KEY']}
    
    # Query AF and get the tag info to be stored in our local ES cache
    app.logger.debug(f'Gathering tag info for {tagName}')
    queryResponse = requests.post(url=searchURL,headers=headers,
                                  data=json.dumps(data))
    queryData = queryResponse.json()
        
    return queryData



def processTagList(tagObj):    
    tagList = list()
    sample = tagObj['_source']

    # If we have tags associated with samples, extract them for each 
    # sample and then get their meta-data
    if 'tag' in sample:
        app.logger.debug(f"Found tag(s) {sample['tag']} in sample")
        
        for tagName in sample['tag']:
            app.logger.debug(f"Processing tag {tagName}")
            
            tagData = processTag(tagName)
            tagList.append(tagName)
            
            app.logger.debug(f"{tagData}")
    else:
        tagList = "NULL"

    return tagList     



def processTag(tagName):
    '''
    Method determines if we have a local tag info cache or we need to go to AF 
    and gather the info.  Returns the data for manipulation by the calling
    method
    '''
    tagDoc = False
    updateDetails = False
    afApiKey = app.config['AUTOFOCUS_API_KEY']
    #cacheTimeout = app.config['AF_TAG_INFO_MAX_AGE']
    retStatusFail = f'Failed to get info for {tagName} - FAIL'
    #now = datetime.datetime.now()
    timeLimit = (datetime.datetime.now() - 
                    datetime.timedelta(days=app.config['DOMAIN_TAG_INFO_MAX_AGE']))

    app.logger.debug(f"Querying local cache for {tagName}")


    try:
        tagDoc = TagDetailsDoc.get(id=tagName)

        # check age of doc and set to update the details
        print(f"Time calculated: {timeLimit > tagDoc.updated_at}")
        if timeLimit > tagDoc.updated_at:
            print("need to update")
        else:
            print("no need to update tagDoc")
            updateDetails = True
            updateType = "Updating"

    except NotFoundError as nfe:
        app.logger.info(f"Making new doc for tag {tagName}")
        updateDetails = True
        updateType = "Creating"


    if updateDetails:  
        
        afTagData = getTagInfo(tagName)
        
        # If we get the word 'message' in the return it means something went
        # wrong, so just return False
        if "message" not in afTagData:
            app.logger.debug(f"{updateType} doc for {tagName}")

            tagDoc = TagDetailsDoc(meta={'id': tagName},name=tagName)
            tagDoc.tag = afTagData['tag']
            tagDoc.updated_at = datetime.datetime.now().isoformat(' ')
            tagDoc.type_of_doc = "tag-doc"
            tagDoc.processed = 1
            # Only set the created_at attribute if we aren't updating 
            if updateType == "Creating":
                tagDoc.created_at = datetime.datetime.now().isoformat(' ')
            tagDoc.save()
            
            tagDoc = TagDetailsDoc.get(id=tagName)

        else:
            return False
    
    return (tagDoc.tag['tag_name'],tagDoc.tag['public_tag_name'],
            tagDoc.tag['tag_class'],tagDoc.tag['updated_at'])
    


def getDomainInfo(threatDomain):
    '''
    Method that uses user supplied api key (.panrc) and gets back a "cookie."  
    Loops through timer (in minutes) and checks both the timer value and the 
    maximum search result percentage and returns the gathered domain data when 
    either of those values are triggered
    '''
    apiKey= app.config['AUTOFOCUS_API_KEY']
    searchURL = app.config["AUTOFOCUS_SEARCH_URL"]
    resultURL = app.config["AUTOFOCUS_RESULTS_URL"]
    lookupTimeout = app.config["AF_LOOKUP_TIMEOUT"]
    maxPercentage = app.config["AF_LOOKUP_MAX_PERCENTAGE"]
    resultData = {"apiKey": apiKey}
    headers = {"Content-Type": "application/json"}
    searchData = {"apiKey": apiKey, 
                    "query": {
                        "operator": "all", 
                        "children": [{
                            "field":"alias.domain",
                            "operator":"contains",
                            "value": threatDomain}]}, 
                    "size": 10, 
                    "from": 0,
                    "sort": {"create_date": {"order": "desc"}}, 
                    "scope": "global", 
                    "artifactSource": "af"}
    
    # Query AF and it returns a "cookie" that we use to view the resutls of the 
    # search
    app.logger.debug(f'Gathering domain info for {threatDomain}')
    queryResponse = requests.post(url=searchURL,headers=headers,
                                  data=json.dumps(searchData))
    app.logger.debug(f"Initial AF domain query returned {queryResponse.json()}")
    queryData = queryResponse.json()
    
    if queryData['af_cookie']:
        cookie = queryData['af_cookie']
        cookieURL = resultURL + cookie
    
        app.logger.debug(f"Cookie {cookie} returned on query for {threatDomain}")

        # Wait for the alloted time before querying AF for search results.  Do check
        # every minute anyway, in case the search completed as the cookie is only 
        # valid for 2 minutes after it completes. 
        for timer in range(lookupTimeout):
            time.sleep(60)
            cookieResults = requests.post(url=cookieURL,headers=headers,
                                        data=json.dumps(resultData))
            domainData = cookieResults.json()
            if domainData['af_complete_percentage'] >= maxPercentage :
                updateAfStats(domainData['bucket_info'])
                break
            else:
                updateAfStats(domainData['bucket_info'])
                app.logger.info(f"Search completion " +
                                f"{domainData['af_complete_percentage']}% for " +
                                f"{threatDomain} at {timer+1} minute(s): " +
                                f"{domainData}")

    else:
        app.logger.error(f"Unable to retrieve domain info from AutoFocus. " +
                         f"The AF query returned {queryData}")

    domainTags = list()

    if domainData['total'] !=0:
        for hits in domainData['hits']:
            tagList = processTagList(hits)
            print(tagList)
            #domainObj.appendhits['finish_date']
                #domainTags.append(hits['_source'])
    else:
        app.logger.debug(f"No samples found for {threatDomain} in time allotted")
        
    exit()
    return domainHits

