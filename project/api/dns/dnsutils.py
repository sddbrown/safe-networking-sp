
import json
import time
import requests
import datetime
from project import app
from ast import literal_eval
from pprint import pprint as pp
from elasticsearch.exceptions import NotFoundError
from project.api.dns.dns import AFDetailsDoc, TagDetailsDoc, DomainDetailsDoc
from elasticsearch_dsl import DocType, Search, Date, Integer, Keyword, Text, Ip, connections



def updateAfStats(afInfo):
    '''
    Update the sfn-details af-doc. 
    If it doesn't exist, the 'upsert' does that for us. 
    '''
    # Define a default Elasticsearch client
    #connections.create_connection(hosts=[app.config['ELASTICSEARCH_HOST']])
    now = datetime.datetime.now()

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
            tagList.append(tagData)
            
            app.logger.debug(f"Tag data returned from processTag(): {tagData}")
    else:
        tagData = "NULL"

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
    now = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
    timeLimit = (datetime.datetime.now() - 
                    datetime.timedelta(days=app.config['DOMAIN_TAG_INFO_MAX_AGE']))

    app.logger.debug(f"Querying local cache for {tagName}")


    try:
        tagDoc = TagDetailsDoc.get(id=tagName)

        # check age of doc and set to update the details
        if timeLimit > tagDoc.doc_updated:
            app.logger.debug(f"Last updated can't be older than {timeLimit} " +
                             f"but it is {tagDoc.doc_updated} and we need to " +
                             f"update cache")
            updateDetails = True
            updateType = "Updating"
        else:
            app.logger.debug(f"Last updated can't be older than {timeLimit} " +
                             f"and {tagDoc.doc_updated} is not, so don't need" +
                             f" to update cache")
            

    except NotFoundError as nfe:
        app.logger.info(f"No local cache found for tag {tagName}")
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
            tagDoc.doc_updated = now
            tagDoc.type_of_doc = "tag-doc"
            tagDoc.processed = 1
            # Only set the doc_created attribute if we aren't updating 
            if updateType == "Creating":
                tagDoc.doc_created = now
            print(f"tagDoc is {tagDoc.to_dict()} ")
            tagDoc.save()
            
            tagDoc = TagDetailsDoc.get(id=tagName)

        else:
            return False
    
    return (tagDoc.tag['tag_name'],tagDoc.tag['public_tag_name'],
            tagDoc.tag['tag_class'])
    


def assessTags(tagsObj):
    '''
    Determine the most relevant tag based on samples and the dates associated
    with the tag.  Utilizes the CONFIDENCE_LEVELS dictionary set in the .panrc
    or the default values for confidence scoring
    '''
    confLevel = 5
    taggedEvent = False
    tagConfLevels = literal_eval(app.config['CONFIDENCE_LEVELS'])

    # Iterate over all tags until:
    #  Find a tag with campaign
    #    We're done and return
    #  Find an actor
    #    Set the tagInfo to this but keep going in case we find a campaign
    #  Find the *first* malware
    #    Set the tagInfo to this but keep going in case we find a campaign 
    #      or an actor 

    # import pdb
    # pdb.set_trace()

    # print(tagsObj)

    # print(f"len of tagsObj is {len(tagsObj)}")
    for entry in tagsObj:
        # print(f"entry is {entry}")
        while not taggedEvent:
            sampleDate = entry[0]
            # print("\n\n\n")
            # print(f"sample date is {sampleDate}")
            sampleFileType = entry[1]
            for tag in entry[2]:
                tagName = tag[1]
                tagClass = tag[2]
                
                app.logger.debug(f"Working on tag {tagName} " +
                                 f"with class of {tagClass}")
                
                if tagClass == "campaign":
                    tagInfo = {"tag_name":tagName,"public_tag_name":tag[0],
                               "tag_class":tagClass,"sample_date":sampleDate,
                               "file_type":sampleFileType, 
                               "confidence_level":90}
                    taggedEvent = True
                    app.logger.debug(f"Tag info for {tagName}: {pp(tagInfo)}")
                    break   # This the grand daddy of all tags 
                            # No need to keep processing the rest
                    
                elif tagClass == "actor":
                    tagInfo = {"tag_name":tagName,"public_tag_name":tag[0],
                               "tag_class":tagClass,"sample_date":sampleDate,
                               "file_type":sampleFileType, 
                               "confidence_level":90}
                    taggedEvent = True
                    app.logger.debug(f"Tag info for {tagName}: {pp(tagInfo)}")


                elif (tagClass == "malware_family") and not taggedEvent:
                   
                    # Figure out the confidence level for the malware based on how 
                    # many days old it is. 
                    dateDiff = (datetime.datetime.now() - datetime.datetime.strptime(sampleDate, "%Y-%m-%dT%H:%M:%S"))
                    
                    app.logger.debug(f"Calculating confidence level: " +
                                     f"Day differential of {dateDiff.days}")
                
                    for days in tagConfLevels:
                        if dateDiff.days < int(days):
                            confLevel = tagConfLevels[days]
                            app.logger.debug(f"confidence_level for " +
                                        f"{tagName} @ date " +
                                        f"{sampleDate}: "+
                                        f"{confLevel} based on" +
                                        f" age of {dateDiff.days}")
                            break # We found the right confidence level
                        else:
                            confLevel = 5
                            app.logger.debug(f"confidence_level for " +
                                            f"{tagName} @ date " +
                                            f"{sampleDate}: "+
                                            f"{confLevel} based on" +
                                            f" age of {dateDiff.days}")

                    tagInfo = {"tag_name":tagName,"public_tag_name":tag[0],
                                "tag_class":tagClass,"sample_date":sampleDate,
                                "file_type":sampleFileType, 
                                "confidence_level":confLevel}
                    taggedEvent = True
                    app.logger.debug(f"Tag info for {tagName}: {tagInfo}")
                   
            # Went through all the tags available and none were of interest    
            if not taggedEvent:    
                tagInfo = dict.fromkeys(['public_tag_name','tag_name','tag_class','sample_date',"confidence_level"])
                tagInfo['public_tag_name'] = "Not Available"
                tagInfo['tag_name'] = "Not Available"
                tagInfo['tag_class'] = "Not Available"
                tagInfo['sample_date'] = "00-00-00T00:00:00:00"
                tagInfo['confidence_level'] = confLevel
                taggedEvent = True
            

    return tagInfo  



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
    
        app.logger.debug(f"Cookie {cookie} returned for query of {threatDomain}")

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
    domainObj = list()

    if domainData['total'] !=0:
        for hits in domainData['hits']:
            tagList = processTagList(hits)
            domainObj.append((hits['_source']['finish_date'],
                             hits['_source']['filetype'],
                             tagList))
           
    else:
        app.logger.debug(f"No samples found for {threatDomain} in time allotted")
        domainObj.append(("00-00-00T00:00:00:00","None","Not Available for Domain",
                         "Not Available for Domain", "Not Available for Domain"))
    
    return domainObj



def getDomainDoc(domainName):
    '''
    Method to get the local domain doc info and return it to the event 
    processor so it can update the event with the most recent info
    '''
    updateDetails = False
    now = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
    timeLimit = (datetime.datetime.now() - 
                    datetime.timedelta(days=app.config['DNS_DOMAIN_INFO_MAX_AGE']))

    app.logger.debug(f"Querying local cache for {domainName}")


    try:
        domainDoc = DomainDetailsDoc.get(id=domainName)
        
        # check age of doc and set to update the details
        if timeLimit > domainDoc.doc_updated:
            app.logger.debug(f"Last updated can't be older than {timeLimit} " +
                             f"but it is {domainDoc.doc_updated} and we need to " +
                             f"update cache")
            updateDetails = True
            updateType = "Updating"
        else:
            app.logger.debug(f"Last updated can't be older than {timeLimit} " +
                             f"and {domainDoc.doc_updated} is not, so don't need" +
                             f" to update cache")

    except NotFoundError as nfe:
        app.logger.info(f"No local cache doc found for domain {domainName}")
        updateDetails = True
        updateType = "Creating"


    # Either we don't have it or we determined that it's too old
    if updateDetails:
        app.logger.info(f"Making new doc for domain {domainName}")
        afDomainData = getDomainInfo(domainName)
        domainDoc = DomainDetailsDoc(meta={'id': domainName},name=domainName)

        domainDoc.tags = afDomainData
        domainDoc.doc_created = now
        domainDoc.doc_updated = now
        domainDoc.type_of_doc = "domain-doc"
        domainDoc.save()
        
    app.logger.debug(f"Local domain doc contains: {domainDoc}")

    return domainDoc