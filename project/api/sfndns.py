import sys
import json
import time
import datetime
import requests
from random import randint
from project import app, es
from collections import OrderedDict
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
from project.api.utils import calcCacheTimeout
from elasticsearch import TransportError, RequestError, ElasticsearchException


def getDomainInfo(threatDomain,apiKey):
    '''
    Method that uses user supplied api key (instance/.panrc) and gets back a 
    "cookie."  Loops through timer (in minutes - set in instance/.panrc) and
    checks both the timer value and the maximum search result percentage and 
    returns the gathered domain data when either of those values are triggered
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
    queryData = queryResponse.json()
    cookie = queryData['af_cookie']
    cookieURL = resultURL + cookie
    app.logger.debug(f"Cookie {cookie} returned on query for {threatDomain}" + 
                     f" using {cookieURL}")

    # Wait for the alloted time before querying AF for search results.  Do check
    # every minute anyway, in case the search completed as the cookie is only 
    # valid for 2 minutes after it completes. 
    for timer in range(lookupTimeout):
        time.sleep(60)
        cookieResults = requests.post(url=cookieURL,headers=headers,
                                      data=json.dumps(resultData))
        domainData = cookieResults.json()
        if domainData['af_complete_percentage'] >= maxPercentage :
            break
        else:
            app.logger.info(f"Search completion " +
                            f"{domainData['af_complete_percentage']}% for " +
                            f"{threatDomain} at {timer} minute(s)")

    
    return domainData

def getTagInfo(tagName,apiKey):
    '''
    Method that uses user supplied api key (.panrc) and gets back the info on
    the tag specified as tagName.  This doesn't take very long so we don't have
    to do all the crap we did when getting domain info
    '''
    searchURL = app.config["AUTOFOCUS_SEARCH_URL"] + f"tag/{tagName}"
    headers = {"Content-Type": "application/json"}
    searchData = {"apiKey": apiKey}
    #               "scope": "global",
    #               "pageNum": 0,
    #               "pageSize": 3,
    #               "sortBy": "name",
    #               "order": "asc",
    #               "query":{"field": "tag_name",
    #                        "operator": "is",
    #                        "value": tagName}
    #              }
    
    # Query AF and it returns a "cookie" that we use to view the resutls of the 
    # search
    app.logger.debug(f'Gathering tag info for {tagName}')
    queryResponse = requests.post(url=searchURL,headers=headers,
                                  data=json.dumps(searchData))
    queryData = queryResponse.json()
        
    return queryData


def processTag(tagName):
    '''
    Method determines if wehave a local tag info cache or we need to go to AF 
    and gather the info.  Returns the data for manipulation by the calling
    method
    '''
    retStatusFail = f'Failed to get info for {tagName} - FAIL'
    afApiKey = app.config['AUTOFOCUS_API_KEY']
    cacheTimeout = app.config['AF_TAG_INFO_MAX_AGE']

    # Sleep for a random time because of the multiprocessing, if we don't we  
    # may actually create the same details doc more than once.  Hopefully 
    # this will avoid that situation
    time.sleep(randint(1,6))

    app.logger.debug(f"Querying local cache for {tagName}")
    # Search to see if we already have a details doc for the tag
    detailsDoc = es.search(index='sfn-details',doc_type='doc',
                           body={
                            "query": {
                                "bool": {
                                "must": [{"term": {"type": "tag-doc"}},
                                         {"term": {"name.keyword": tagName}}]}}}
                           )

    app.logger.debug(f"Here is the local cache query result for {tagName}: " +
                     f"{detailsDoc}")

    # We don't have the tag info in ES, so create the doc associated with it
    if detailsDoc['hits']['total'] == 0:
        app.logger.debug(f"Local cache for {tagName} being created")

        indexLocal = 3
        now = datetime.datetime.now()
        createTime = now.strftime('%Y-%m-%dT%H:%M:%SZ')

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
            indexLocal = 3
            app.logger.debug(f"{tagName} has a cache but needs to be updated")
        else:
            indexLocal = 1
            tagData = detailsDoc
            app.logger.debug(f"{tagName} has a cache and is within limits")
        
    if indexLocal == 3:
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

    # Set the doc's processed flag to 17 in ES, meaning we at least try it 
    try:
        es.update(index='sfn-details',doc_type='doc',id=tagDoc,
                    body={"doc": {"processed": 17}})
    except TransportError as te:
        app.logger.error(f'Unable to communicate with ES server -{te.info}')
        return retStatusFail
    except RequestError as re:
        app.logger.error(f'Unable to update {tagDoc} - {re.info}')
        return retStatusFail

    # call getDomainInfo() and if successful, parse out the info, replace the 
    # current data and update the last_updated value to now

    app.logger.debug(f"Query to obtain gather tag info for " + 
                        f"{tagName}")
    tagData = getTagInfo(tagName,afApiKey)
    app.logger.debug(f"Details retreived from getTagInfo(): {tagData}")
    if 'FAIL' in tagData:    
        app.logger.error(f"Unable to get tag info for {tagName}")
        return retStatusFail

    try:
        es.update(index='sfn-details',doc_type='doc',id=tagDoc,
                    body={"doc": {
                            "processed": 1,
                            "tags": tagData['tags']}})
        return tagData
    
    except TransportError as te:
        app.logger.error(f'Unable to communicate with ES server -{te.info}')
        return retStatusFail
    except RequestError as re:
        app.logger.error(f'Unable to update {tagDoc} - {re.info}')
        return retStatusFail
    

def updateDetailsDomainDoc(domainDoc,threatDomain):
    '''
    Method used to update the sfn-details document (dns-doc type) in ES so that 
    we have a "cached" version of the domain details and we don't have to go to 
    AF all the time
    calls getDomainInfo()
    '''
    retStatusFail = f'{domainDoc} - FAIL'
    retStatusPass = f'{domainDoc} - PASS'
    afApiKey = app.config['AUTOFOCUS_API_KEY']

    # Set the doc's processed flag to 17 in ES, meaning we at least try it 
    try:
        es.update(index='sfn-details',doc_type='doc',id=domainDoc,
                    body={"doc": {"processed": 17}})
    except TransportError as te:
        app.logger.error(f'Unable to communicate with ES server -{te.info}')
        return retStatusFail
    except RequestError as re:
        app.logger.error(f'Unable to update {docID} - {re.info}')
        return retStatusFail

    # call getDomainInfo() and if successful, parse out the info, replace the 
    # current data and update the last_updated value to now
    try:
        app.logger.debug(f"Query to obtain gather domain info for " + 
                         f"{threatDomain}")
        domainDetails = getDomainInfo(threatDomain,afApiKey)
        sampleDict = OrderedDict()
        entryDict = OrderedDict()
        tagList = list()

        for item in domainDetails['hits']:
            tagList = []
            record = item['_source']
            entryDate = record['finish_date']
            for tagName in record['tag']:
                app.logger.debug(f"Processing tag {tagName} for {domainDoc}")
                tagData = processTag(tagName)
                tagList.append(tagName)
                app.logger.debug(f"{tagData}")
            entryDict[entryDate] = tagList

        app.logger.debug(f"Dump of entryDict - {json.dumps(entryDict)}")    

        return True
    except KeyError as error:
        app.logger.error(f"Unable to retrieve AutoFocus API key. Returned {error} when getting domain info for {threatDomain}")
        return retStatusFail


def searchDomain(docID):
    '''
    Function that discerns if we have the domain locally cached in the ES DB and
    if we don't (or the cache timeout has elapsed) go and update the sfn-details 
    index document for that domain.  This prevents us from going to AF 
    unneccessarily and will make SFN much faster on updates if we already have 
    the domain in the DB
    '''
    indexLocal = 3
    retStatusFail = f'{docID} - FAIL'
    retStatusPass = f'{docID} - PASS'
    cacheTimeout = app.config['DNS_DOMAIN_INFO_MAX_AGE']

    app.logger.info(f"Starting process {docID}")
    app.logger.debug(f"{docID} - changing field 'process' to 17")

    # Set the doc's processed flag to 17 meaning we at least try it 
    try:
        es.update(index='sfn-dns-event',doc_type='doc',id=docID,
                    body={"doc": {"processed": 17}})
    except TransportError as te:
        app.logger.error(f'Unable to communicate with ES server -{te.info}')
        return retStatusFail
    except RequestError as re:
        app.logger.error(f'Unable to update {docID} - {re.info}')
        return retStatusFail
    
    # Get the domain associated with the event doc
    try:
        eventDoc = es.get(index="sfn-dns-event",doc_type="doc",
                                id=docID,_source="domain_name")
        threatDomain = eventDoc['_source']['domain_name']
        app.logger.debug(f"Search for domain in {docID} found {threatDomain}")
    except TransportError as te:
        app.logger.error(f'Unable to communicate with ES server -{te.info}')
        return retStatusFail
    except RequestError as re:
        app.logger.error(f'Unable to find domain in {docID} - {re.info}')
        return retStatusFail

    # Sleep for a random time because of the multiprocessing, if we don't we  
    # may actually create the same details doc more than once.  Hopefully 
    # this will avoid that situation
    time.sleep(randint(1,6))

    # See if we have the domain info already, if not, go get it
    try:
        detailsDoc = es.search(index='sfn-details',
                               body={
                                "query": {
                                  "bool": {
                                    "must": [{
                                      "match": {"type": "domain-doc"},
                                      "match": {"name.keyword": threatDomain}}]}}})
        
        # We don't have the domain in ES, so create the doc associated with it
        if detailsDoc['hits']['total'] == 0:
            indexLocal = 3
            now = datetime.datetime.now()
            createTime = now.strftime('%Y-%m-%dT%H:%M:%SZ')
            ret = es.index(index='sfn-details', doc_type='doc',
                           body={"type": "domain-doc",
                                 "name": threatDomain, 
                                 "last_updated": "2000-01-01T12:00:00Z",
                                 "processed": 0,
                                 "create_time": createTime})
            domainDoc = ret['_id']
            app.logger.info(f'Local cache for {threatDomain} created: {domainDoc}')

        # We have a domain doc in ES 
        else:
            domainDoc = detailsDoc['hits']['hits'][0]['_id']
            foundDomain = detailsDoc['hits']['hits'][0]['_source']['name']
            lastUpdated = detailsDoc['hits']['hits'][0]['_source']['last_updated']
            
            # If the doc last_updated is older than the setting, update it
            if (calcCacheTimeout(cacheTimeout,lastUpdated,domainDoc)) is not True:
                indexLocal = 3
            elif (foundDomain == threatDomain):
                indexLocal = 1
                app.logger.debug(f"Associating {threatDomain} in event " +
                                 f"{docID} with {domainDoc}")
            else:
                # We should never get here
                app.logger.info(f'Searching doc {docID} gives {threatDomain}')
                return retStatusFail
        
        # Update the domain details doc
        if indexLocal == 3:
            retCode = updateDetailsDomainDoc(domainDoc,threatDomain)
            if "FAIL" in retCode:
                app.logger.error(f"Unable to update domain: {threatDomain}")
                return retStatusFail
        # if indexLocal == 1:
            # tagUpdate = es.get(index="sfn-details",doc_type="domain-doc",id=domainDoc,_source="tags")
            # es.update(index='sfn-dns-event', doc_type='doc',id=docID,body={"doc": {"tag": tagUpdate}})

        app.logger.debug(f"Return from updateDetailsDomainDoc() is {retCode}")
        return retStatusPass
    except TransportError as te:
        app.logger.error(f'Unable to communicate with ES server -{te.info}')
        return retStatusFail
    except RequestError as re:
        app.logger.error(f'Unable to update {docID} - {re.info}')
        return retStatusFail
   
    # Second check to see if we already have the domain in sfn-dns-domains index
    #  If we do, set variable index-local var to 1.
    #   Next check the age of the index and see if it needs updating and set index-local
    #   variable to 3 so it will update it.
    #  Else we do not have it locally and will need to call AF for it.
    #   create the index for the domain name 
    #   set variable index-local to 3 so it can go to AF and update
    #  If variable index-local is set to 3 go to AF and update the index for 
    #    that domain and set variable index-local to 1
    # 
    # If index-local is 1 (it better be) then reference the sfn-dns-domains doc ID
    #   in the sfn-dns-event doc so that we can later look up the pertinatent data
    #   and tags for that domain against that event.  
    #  
    #  PRAY
    #
    #  
    #     


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
                                        {"match": {"processed": "0"}}] # end must
                                 }  # end bool
                              }
                           }   # end body
                        )

        app.logger.info(f"Found {docs['hits']['total']} unpropcessed documents for sfn-dns-event")


        for entry in docs['hits']['hits']:
            docKey = entry['_id']
            if entry['_source']['threat_name'] == "generic":
                secDocIds[docKey] = entry['_source']['domain_name']
                app.logger.debug(f"{docKey} : {secDocIds[docKey]} - {entry['_source']['threat_name']}")
            else:
                priDocIds[docKey] = entry['_source']['domain_name']
                app.logger.debug(f"{docKey} : {priDocIds[docKey]} - {entry['_source']['threat_name']}")
                       
        app.logger.info(f"Found {len(priDocIds)} known threats")
        app.logger.info(f"Found {len(secDocIds)} 'generic' threats")
        
        # multiprocessing.Pool will take any iterable but it changes it to a list,
        # so in our case, the keys get pulled and sent as a list.  This is a 
        # bummer because the searchDomain is going to have to do the same 
        # lookup (that we just fricken did) to find the domain name.  Need to
        # find a better way to do this to prevent more lookups.  
       
        # Multiprocess the primary keys
        with Pool(cpu_count() * 2) as pool:
            results = pool.map(searchDomain, priDocIds)
        
        app.logger.debug(results)
        
        # Do the same with the generic/secondary keys and pace so we don't kill AF
        with Pool(cpu_count() * 2) as pool:
            results = pool.map(searchDomain, secDocIds)
        
        app.logger.debug(results)

    except TransportError:
        app.logger.warning('Initialization was unable to find the index sfn-dns-event')
    

def main():
    pass

if __name__ == "__main__":
    main()
    