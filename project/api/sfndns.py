import sys
import json
import time
import datetime
import requests
from random import randint
from project import app, es
from project.api.utils import *
from collections import OrderedDict
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
from elasticsearch import TransportError, RequestError, ElasticsearchException


def getTagInfo(tagName,apiKey):
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
    data = {"apiKey": apiKey}
    
    # Query AF and get the tag info to be stored in our local ES cache
    app.logger.debug(f'Gathering tag info for {tagName}')
    queryResponse = requests.post(url=searchURL,headers=headers,
                                  data=json.dumps(data))
    queryData = queryResponse.json()
        
    return queryData



def processTag(tagName):
    '''
    Method determines if wehave a local tag info cache or we need to go to AF 
    and gather the info.  Returns the data for manipulation by the calling
    method
    '''
    updateLocalDoc = True
    afApiKey = app.config['AUTOFOCUS_API_KEY']
    cacheTimeout = app.config['AF_TAG_INFO_MAX_AGE']
    retStatusFail = f'Failed to get info for {tagName} - FAIL'

    app.logger.debug(f"Querying local cache for {tagName}")

    # Sleep for a random time because of the multiprocessing, if we don't we  
    # may actually create the same details doc more than once.  Hopefully 
    # this will avoid that situation
    time.sleep(randint(1,12))
    
    # Search to see if we already have a details doc for the tag
    detailsDoc = es.search(index='sfn-details',doc_type='doc',
                           body={
                            "query": {
                              "bool": {
                              "must": [{"term": {"type": "tag-doc"}},
                                       {"term": {"name.keyword": tagName}}]}}})

    app.logger.debug(f"Local cache query result for {tagName}: {detailsDoc}")

    # We don't have the tag info in ES, so create the doc associated with it
    if detailsDoc['hits']['total'] == 0:
        app.logger.debug(f"Local cache for {tagName} being created")
        updateLocalDoc = True
        createTime = getNow()

        ret = es.index(index='sfn-details',doc_type='doc',
                        body={"type": "tag-doc", 
                              "name": tagName,
                              "last_updated": "2000-01-01T12:00:00Z",
                              "processed": 0,
                              "create_time": createTime})
        tagDoc = ret['_id']

        app.logger.info(f"Local cache for {tagName} created: {tagDoc}")

    # We have a local cache of the tag in ES 
    else:
        tagDoc = detailsDoc['hits']['hits'][0]['_id']
        foundTag = detailsDoc['hits']['hits'][0]['_source']['name']
        lastUpdated = detailsDoc['hits']['hits'][0]['_source']['last_updated']
        
        # If the doc last_updated is older than the setting, update it
        if (calcCacheTimeout(cacheTimeout,lastUpdated,tagDoc)) is not True:
            updateLocalDoc = True
            app.logger.debug(f"{tagName} has a cache but needs to be updated")
        else:
            updateLocalDoc = False
            tagData = detailsDoc
            app.logger.debug(f"{tagName} has a cache and is within limits")
        
    if updateLocalDoc:
        tagData = updateDetailsTagDoc(tagDoc,tagName)
        if 'FAIL' in tagData:
            print(f"Unable to update tag: {tagName}")
            return retStatusFail
    
    return tagData



def updateDetailsTagDoc(tagDoc, tagName):
    '''
    Method used to update the sfn-details document (tag-doc type) in ES so that 
    we have a "cached" version of the tag details and we don't have to go to 
    AF all the time
    '''
    retStatusFail = f"Update of {tagDoc} - FAIL"
    afApiKey = app.config['AUTOFOCUS_API_KEY']
    updateTime = getNow()

    # Set the doc's processed flag to 17 in ES, meaning we at least try it 
    try:
        setDocProcessing('sfn-details',tagDoc)
    except Exception as de:
       raise Exception(f"{retStatusFail}: {de}")

    # Call getTagInfo() and if successful, parse out the info, replace the 
    # current data and update the last_updated value to now
    tagData = getTagInfo(tagName,afApiKey)
    app.logger.debug(f"Details retreived from getTagInfo(): {tagData}")
   
    # Got tagData from AF and we can push it to the local tagDoc
    if 'FAIL' not in tagData: 
        updateAfStats(tagData['bucket_info'])
        try:
            es.update(index='sfn-details',doc_type='doc',id=tagDoc,
                      body={"doc": {
                              "processed": 1,
                              "last_updated": updateTime,
                              "tag": tagData['tag']}})
        
        except TransportError as te:
            app.logger.error(f'Unable to communicate with ES server -{te.info}')
            raise Exception(f"{retStatusFail}: {te.info}")
        except RequestError as re:
            app.logger.error(f'Unable to update {tagDoc} - {re.info}')
            raise Exception(f"{retStatusFail}: {re.info}")
    else:    
        app.logger.error(f"Unable to get tag info for {tagName}")
        raise Exception(f"{retStatusFail} for {tagName}")

    # Made it through all that and we have the tagData
    return tagData



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


    
def classifyTagData(tagDict):
    '''
    Takes a dictionary of keys and tags associated tags with each key.  Returns
    a json formatted hierarchy with the key being the initial key sent, 
    each tag classified as malware, malicious behavior, exploit, campaign or 
    actor    
    '''
    tagFormattedList = list()
    
    for key in tagDict:
        for tagName in tagDict[key]:
            app.logger.debug(f"Working with tag {tagName}")
            tagInfo = dict.fromkeys(['public_tag_name','tag_name',
                                     'tag_class','updated_at'])
            detailsDoc = es.search(index='sfn-details',doc_type='doc',
                           body={
                            "query": {
                              "bool": {
                              "must": [{"term": {"type": "tag-doc"}},
                                       {"term": {"name.keyword": tagName}}]}}})

            print("\n\n\n" + json.dumps(detailsDoc) + "\n\n\n")
            if detailsDoc['hits']['total'] != 0:
                app.logger.debug(f"Source for detailsDoc {detailsDoc['hits']['hits'][0]}")
                tagInfo['public_tag_name'] = detailsDoc['hits']['hits'][0]['_source']['tag']['public_tag_name']
                tagInfo['tag_name'] = detailsDoc['hits']['hits'][0]['_source']['tag']['tag_name']
                tagInfo['tag_class'] = detailsDoc['hits']['hits'][0]['_source']['tag']['tag_class']
                tagInfo['updated_at'] = f"{key}Z"
                tagFormattedList.append(tagInfo)
            # For so reason we don't have the tag doc - which is weird
            else:
                tagData = processTag(tagName)
                tagInfo['public_tag_name'] = tagData['hits']['hits'][0]['_source']['tag']['public_tag_name']
                tagInfo['tag_name'] = tagData['hits']['hits'][0]['_source']['tag']['tag_name']
                tagInfo['tag_class'] = tagData['hits']['hits'][0]['_source']['tag']['tag_class']
                tagInfo['updated_at'] = f"{key}Z"


        app.logger.debug(f"Created tagFormattedList of {tagFormattedList}")
        
    return tagFormattedList



def getDomainInfo(threatDomain,apiKey):
    '''
    Method that uses user supplied api key (.panrc) and gets back a "cookie."  
    Loops through timer (in minutes) and checks both the timer value and the 
    maximum search result percentage and returns the gathered domain data when 
    either of those values are triggered
    '''
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
    app.logger.debug(f"Inittial AF domain query returned {queryResponse.json()}")
    queryData = queryResponse.json()
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

    
    return domainData


def updateDetailsDomainDoc(domainDoc,threatDomain):
    '''
    Function used to update the sfn-details document (dns-doc type) in ES so 
    we have a "cached" version of the domain details and we don't have to go to 
    AF all the time, 
    calls:
        setDocProcessing()
        getDomainInfo()
        processTagList()
        classifyTagData()
    '''
    entryDict = OrderedDict()
    retStatusFail = f'{domainDoc} - FAIL'
    retStatusPass = f'{domainDoc} - PASS'
    afApiKey = app.config['AUTOFOCUS_API_KEY']

    # Set the doc's processed flag to 17 in ES, meaning we at least try it 
    try:
        setDocProcessing('sfn-details',domainDoc)
    except Exception as de:
       raise Exception(f"{retStatusFail} for {domainDoc}: {de}")
    
    # Call getDomainInfo() and if successful, parse out the info, replace the 
    # current data and update the last_updated value to now
    app.logger.debug(f"calling getDomainInfo() for {threatDomain}")

    domainDetails = getDomainInfo(threatDomain,afApiKey)


    # Make sure we got tags back in the domainDetails
    if domainDetails['total'] != 0: 
        # For each 'sample' entry associated with the domain
        for entry in domainDetails['hits']:
            entryDict[entry['_source']['finish_date']] = processTagList(entry)           
            app.logger.debug(f"Sending to classifyTagData(): {entryDict}")

            # Classify the tags that we have against the data stored in ES
            # and then parse it and add to the domain info
            tagData = classifyTagData(entryDict)
            app.logger.debug(f"Received from classifyTagData() - {tagData}")
            
            #Now that we have the tag data, associate it with the domain
            updateTime = getNow()
            try:
                es.update(index='sfn-details',doc_type='doc',id=domainDoc,
                            body={"doc": {
                                    "processed": 1,
                                    "last_updated": updateTime,
                                    "sample_tags": tagData}})

            except TransportError as te:
                app.logger.error(f'Unable to communicate with ES server -{te.info}')
                raise Exception(f"{retStatusFail}: {te.info}")
            except RequestError as re:
                app.logger.error(f'Unable to update {docID} - {re.info}')
                raise Exception(f"{retStatusFail}: {re.info}")

    # Didn't get info back in the time alloted - set it up to be processed again
    else:
        try:
            es.update(index='sfn-details',doc_type='doc',id=domainDoc,
                      body={"doc": {"processed": 0,
                            "sample_tags": [{"updated_at": "2000-01-01T12:00:00Z"}]}})

        except TransportError as te:
            app.logger.error(f'{te.info}')
            raise Exception(f"{retStatusFail}: {te.info}")
        except RequestError as re:
            app.logger.error(f'Unable to update {docID} - {re.info}')
            raise Exception(f"{retStatusFail}: {re.info}")

    return retStatusPass



def searchDomain(docID):
    '''
    Function that discerns if we have the domain locally cached in the ES DB and
    if we don't (or the cache timeout has elapsed) go and update the sfn-details 
    index document for that domain.  This prevents us from going to AF 
    unneccessarily and will make SFN much faster on updates if we already have 
    the domain in the DB
    '''
    
    processedValue = 1
    updateLocalDoc = True
    createTime = getNow()
    retStatusFail = f'{docID} - FAIL'
    retStatusPass = f'{docID} - PASS'
    cacheTimeout = app.config['DNS_DOMAIN_INFO_MAX_AGE']

    app.logger.info(f"Processing event for {docID}")

    # Set the doc's processed flag to 17 in ES, meaning we at least try it 
    try:
        setDocProcessing('sfn-dns-event',docID)
    except Exception as de:
       raise Exception(f"{retStatusFail}: {de}")
       
    # Get the domain associated with the event doc
    try:
        eventDoc = es.get(index="sfn-dns-event",doc_type="doc",id=docID,
                          _source="domain_name")
        
        threatDomain = eventDoc['_source']['domain_name']
        app.logger.debug(f"Search for domain field in {docID} found {threatDomain}")
   
    except TransportError as te:
        app.logger.error(f"Unable to communicate with ES server while " +
                         f"getting domain_name - {te.info}")
        raise Exception(f"{retStatusFail}: {te.info}")
    except RequestError as re:
        app.logger.error(f'Unable to find domain in {docID} - {re.info}')
        raise Exception(f"{retStatusFail}: {re.info}")

    # Sleep for a random time because of the multiprocessing, if we don't we  
    # may actually create the same details doc more than once.  Hopefully 
    # this will avoid that situation
    time.sleep(randint(1,12))

    # See if we have the domain info already, if not, go get it
    try:
        detailsDoc = es.search(index='sfn-details',
                               body={
                                "query": {
                                  "bool": {
                                    "must": [{
                                      "match": {"type": "domain-doc"},
                                      "match": {"name.keyword": threatDomain}
                                      }]}}})

    except TransportError as te:
        app.logger.error(f"Unable to communicate with ES server while " +
                         f"getting domain_name - {te.info}")
        raise Exception(f"{retStatusFail}: {te.info}")
    except RequestError as re:
        app.logger.error(f'Unable to find domain in {docID} - {re.info}')
        raise Exception(f"{retStatusFail}: {re.info}")
        
    # We don't have the domain in ES, so create the doc associated with it
    if detailsDoc['hits']['total'] == 0:
        app.logger.debug(f"No domain-doc for {threatDomain}, creating...")
        updateLocalDoc = True
        
        try:
            ret = es.index(index='sfn-details', doc_type='doc',
                           body={"type": "domain-doc",
                                "name": threatDomain, 
                                "last_updated": "2000-01-01T12:00:00Z",
                                "processed": 0,
                                "sample_tags":[{"tag_name": "Not Processed",
                                                "public_tag_name": "Not Processed",
                                                "tag_class": "Not Processed",
                                                "updated_at":"2000-01-01T12:00:00Z"}],
                                "create_time": createTime})
            domainDoc = ret['_id']
            app.logger.info(f'Local cache for {threatDomain} created: {domainDoc}')
            
            # Created it, now go update it
            retCode = updateDetailsDomainDoc(domainDoc,threatDomain)
            app.logger.debug(f"updateDetailsDomainDoc returned {retCode}")
                
            # The update didn't work since it returned FAIL
            if "FAIL" in retCode:
                app.logger.error(f"Unable to update domain: {threatDomain}")
                raise Exception(f"{retStatusFail}: {retCode}")
            # The update worked and now we have the latest info in ES
            else:
                updateLocalDoc = False  

        except TransportError as te:
                app.logger.error(f"Unable to communicate with ES server while " +
                                f"getting domain_name - {te.info}")
                raise Exception(f"{retStatusFail}: {te.info}")
        except RequestError as re:
            app.logger.error(f'Unable to find domain in {docID} - {re.info}')
            raise Exception(f"{retStatusFail}: {re.info}")

    # We have a domain doc in ES but make sure it has been processed
    elif detailsDoc['hits']['hits'][0]['_source']['processed'] == 1:
        domainDoc = detailsDoc['hits']['hits'][0]['_id']
        foundDomain = detailsDoc['hits']['hits'][0]['_source']['name']
        lastUpdated = detailsDoc['hits']['hits'][0]['_source']['last_updated']
        
        # If the doc last_updated is older than the config setting, 
        # update it 
        if (calcCacheTimeout(cacheTimeout,lastUpdated,domainDoc)) is not True:
            retCode = updateDetailsDomainDoc(domainDoc,threatDomain)
            app.logger.debug(f"updateDetailsDomainDoc returned {retCode}")
                
            # The update didn't work since it returned FAIL
            if "FAIL" in retCode:
                app.logger.error(f"Unable to update domain: {threatDomain}")
                raise Exception(f"{retStatusFail}: {retCode}")
            # The update worked and now we have the latest info in ES
            else:
                updateLocalDoc = False   
        else:
            updateLocalDoc = False
            app.logger.debug(f"Associating {threatDomain} in event-doc " +
                                f"{docID} with domain-doc {domainDoc}")
            
       
    # We have a domain doc, but it is either being processed or is stuck           
    elif detailsDoc['hits']['hits'][0]['_source']['processed'] == 17:
        # Wait or whatever the AF lookup timeout setting is, plus 5 seconds
        time.sleep((app.config['AF_LOOKUP_TIMEOUT'] * 60) + 5)   
        try:
            detailsDoc = es.search(index='sfn-details',
                                body={
                                    "query": {
                                    "bool": {
                                        "must": [{
                                        "match": {"type": "domain-doc"},
                                        "match": {"name.keyword": threatDomain}
                                        }]}}})

            # If this is true, it's still stuck, tell it to update again
            if detailsDoc['hits']['hits'][0]['_source']['processed'] == 17:
                domainDoc = detailsDoc['hits']['hits'][0]['_id']
                retCode = updateDetailsDomainDoc(domainDoc,threatDomain)
                app.logger.debug(f"updateDetailsDomainDoc returned {retCode}")
                    
                # The update didn't work since it returned FAIL
                if "FAIL" in retCode:
                    app.logger.error(f"Unable to update domain: {threatDomain}")
                    raise Exception(f"{retStatusFail}: {retCode}")
                # The update worked and now we have the latest info in ES
                else:
                    updateLocalDoc = False   

        except TransportError as te:
            app.logger.error(f"Unable to communicate with ES server while " +
                            f"getting domain_name - {te.info}")
            raise Exception(f"{retStatusFail}: {te.info}")
        except RequestError as re:
            app.logger.error(f'Unable to find domain in {docID} - {re.info}')
            raise Exception(f"{retStatusFail}: {re.info}")
    
    # If we get here something is wrong and we should update the domain doc
    else:
        domainDoc = detailsDoc['hits']['hits'][0]['_id']
        retCode = updateDetailsDomainDoc(domainDoc,threatDomain)
        app.logger.debug(f"updateDetailsDomainDoc returned {retCode}")
            
        # The update didn't work since it returned FAIL
        if "FAIL" in retCode:
            app.logger.error(f"Unable to update domain: {threatDomain}")
            raise Exception(f"{retStatusFail}: {retCode}")
        # The update worked and now we have the latest info in ES
        else:
            updateLocalDoc = False   

        

    # We should have the latestet (via config settings) domain info.
    # Now, we must determine the tag type that is associated with the 
    # samples and, based on how old the sample is, give a confidence level
    if updateLocalDoc == False:
                    
            domainData = es.get(index="sfn-details",doc_type="doc",id=domainDoc)
            app.logger.debug(f"Retrieved domainData to process tags: " + 
                             f"{domainData}")
           
            # Only do this if there are actually tags in the domain document.
            # Otherwise, set the event to be processed later (55)
            #print(f"WTF2: {domainData['_source']['sample_tags'][0]['updated_at']}")
            
            if "2000-01-01T12:00:00Z" not in domainData['_source']['sample_tags'][0]['updated_at']: 
                tagInfo = assessTags(domainData)
                
                # It couldn't find a relevant tag
                if "00-00-00T00:00:00:00Z" in tagInfo['date']:
                    processedValue =  55
                else:
                    processedValue = 1
        
       

            try:
                es.update(index='sfn-dns-event', doc_type='doc',id=docID,
                          body={"doc": {
                                  "last_updated": createTime,
                                  "processed": processedValue,
                                  "event_tag": tagInfo}})
            except TransportError as te:
                app.logger.error(f"Unable to communicate with ES server while " +
                                f"getting domain_name - {te.info}")
                raise Exception(f"{retStatusFail}: {te.info}")
            except RequestError as re:
                app.logger.error(f'Unable to find domain in {docID} - {re.info}')
                raise Exception(f"{retStatusFail}: {re.info}")
                

    # We should never get here, but just in case
    else:
        app.logger.debug(f"Tried to update the local doc for " + 
                            f"{domainDoc} but something went wrong")
        raise Exception(f"{retStatusFail}: No idea how we got here...")
                        


def processDNS():
    '''
    This function is used to gather the unprocessed docs in ElasticSearch and 
    put them into one of two lists - primary (named threats) or secondary 
    ("generic" threats.  It will process the latest document up to the maximum 
    defined number of documents (DNS_INIT_QUERY_SIZE).  The primary threats will
    be processed in real-time using multiprocessing.  The secondaries will have
    their "processed" value changed to 55.  This value is searched on by the
    process  
    '''
    qSize = app.config["DNS_INIT_QUERY_SIZE"]
    priDocIds = dict()
    secDocIds = dict()

    app.logger.debug(f"Gathering {qSize} sfn-dns-events from ElasticSearch")

    try:
        # Query for the unprocessed DNS entries.  
        docs = es.search(index="sfn-dns-event",
                         body={
                            "size": qSize, 
                            "sort": [{"@timestamp": {"order": "desc"}}], 
                            "query": { 
                                "bool": { 
                                    "must": [
                                        {"match": {"threat_category": "wildfire"}}, 
                                        {"match": {"processed": "0"}}]}}})
    except Exception as e:
        app.logger.error(f"Unable to find the index sfn-dns-event: {e.info}")

    app.logger.info(f"Found {docs['hits']['total']} unpropcessed documents " + 
                    f"for sfn-dns-event")


    # Categorize the entries as either primary (has a threat name) or secondary
    for entry in docs['hits']['hits']:
        docKey = entry['_id']
        if entry['_source']['threat_name'] == "generic":
            secDocIds[docKey] = entry['_source']['domain_name']
            app.logger.debug(f"{docKey} : {secDocIds[docKey]} - " +
                             f"{entry['_source']['threat_name']}")
        else:
            priDocIds[docKey] = entry['_source']['domain_name']
            app.logger.debug(f"{docKey} : {priDocIds[docKey]} - " +
                             f"{entry['_source']['threat_name']}")
                    
    app.logger.info(f"Found {len(priDocIds)} known threats")
    app.logger.info(f"Found {len(secDocIds)} 'generic' threats")

    if not app.config['DEBUG_MODE']:
        '''
        rool.map will take any iterable but it changes it to a list,
        so in our case, the keys get pulled and sent as a list.  This is a 
        bummer because the searchDomain is going to have to do the same 
        lookup (that we just fricken did) to find the domain name.  Need to
        find a better way to do this to prevent more lookups.  
        '''
        # Multiprocess the primary keys
        with Pool(cpu_count() * 4) as pool:
            results = pool.map(searchDomain, priDocIds)
        
        app.logger.debug(results)
        
        # Do the same with the generic/secondary keys and pace so we don't kill AF
        with Pool(cpu_count() * 4) as pool:
            results = pool.map(searchDomain, secDocIds)
        
        app.logger.debug(results)

    # This gets triggered so we only do one document at a time and is for 
    # debugging at a pace that doesn't overload the logs. Load the secondary
    # docs as well, in case we run out of primary while debugging
    else:
        for document in priDocIds:
            try:
                searchDomain(document)
            except Exception as e:
                app.logger.error(f"Exception recieved processing document " +
                                 f"{document}: {e}")
        for document in secDocIds:
            try:
                searchDomain(document)
            except Exception as e:
                app.logger.error(f"Exception recieved processing document " +
                                 f"{document}: {e}")



def main():
    pass



if __name__ == "__main__":
    main()
    