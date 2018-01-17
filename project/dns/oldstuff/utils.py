import time
import datetime
from project import app, es
from ast import literal_eval
from elasticsearch import TransportError, RequestError, ElasticsearchException


def calcCacheTimeout(cacheTimeout,lastDate,docID,format='%Y-%m-%dT%H:%M:%SZ'):
    '''
    Calculate the time difference between two formatted date strings
    '''
    now = datetime.datetime.now()
    lastUpdatedDate = datetime.datetime.strptime(lastDate, format)
    calcDate = calcTimeDiff(now,lastUpdatedDate)

    if calcDate < cacheTimeout:
        app.logger.debug(f"Processing of {docID} gives {calcDate} days vs setting"+ 
                         f" of {cacheTimeout} days")
        return True
    else:
        app.logger.debug(f"Processing of {docID} gives {calcDate} days vs setting"+
                         f" of {cacheTimeout}")
        return False


def calcTimeDiff(eDate,sDate):
       
    if isinstance(eDate,str):
        app.logger.debug(f"Converting {eDate} to date object")
        eDate = datetime.datetime.strptime(eDate,'%Y-%m-%dT%H:%M:%SZ')

    if isinstance(sDate,str):
        app.logger.debug(f"Converting {sDate} to date object")
        sDate = datetime.datetime.strptime(sDate,'%Y-%m-%dT%H:%M:%SZ')

    app.logger.debug(f"Calculating time difference for {eDate} and {sDate}")
    
    return  abs((eDate - sDate).days)


def getNow(returnType="string"):
    '''
    Calculate the current time and send it back in the format needed
    '''
    if returnType == "string":
        return time.strftime('%Y-%m-%dT%H:%M:%SZ')
    elif returnType == "date":
        return datetime.datetime.now()
    else:
        app.logger.debug(f"Return type of {returnType} is not valid, only string or date is valid")
        return "FAIL"


def setDocProcessing(indexName,docID):
    '''
    Helper function to set the document processed field to 17 so that 
    we know it was at least attempted to be processed.
    '''
    app.logger.debug(f"{docID} - changing field 'process' to 17")

    try:
        es.update(index=indexName,doc_type='doc',id=docID,
                  body={"doc": {"processed": 17}})

    except TransportError as te:
        app.logger.error(f"Unable to communicate with ES server while " +
                         f" updating processed to 17 -{te.info}")
        raise Exception(f"Received {te.info} while trying to update {docID}")
    except RequestError as re:
        app.logger.error(f"Unable to update {docID} - {re.info}")
        raise Exception(f"Received {re.info} while trying to update {docID}")

    # Hey, it worked!!
    return "PASS"


def updateAfStats(afInfo):
    '''
    Update the sfn-details af-doc. 
    If it doesn't exist, the 'upsert' does that for us. 
    '''
    try:
        ret = es.update(index='af-details',doc_type='doc',id='af-details',
                  body={"doc": afInfo,
                        "upsert": afInfo})
        app.logger.debug(f"Updating af-details returned {ret}")
        
    except TransportError as te:
        app.logger.error(f"Unable to communicate with ES server while " +
                         f" updating af-details -{te.info}")
    except RequestError as re:
        app.logger.error(f"Unable to update af-details - {re.info}")        


def setDnsTagInfo(tag):
    '''
    Set the "event_tag" info object up so that it can be pushed into ES by
    the calling function
    '''
    app.logger.debug(f"Setting up event_tag object for {tag['tag_name']}")

    tagInfo = dict.fromkeys(['public_name','name','class','date',"confidence_level"])

    tagInfo['public_name'] = tag['public_tag_name']
    tagInfo['name'] = tag['tag_name']
    tagInfo['class'] = tag['tag_class']
    tagInfo['date'] = tag['updated_at']
    tagInfo['confidence_level'] = 17

    return tagInfo


def assessTags(domainData):
    '''
    Determine the most relevant tag based on samples and the dates associated
    with the tag.  Utilizes the CONFIDENCE_LEVELS dictionary set in the .panrc
    or the default values for confidence scoring
    '''
    taggedEvent = False
    tagConfLevels = literal_eval(app.config['CONFIDENCE_LEVELS'])

    app.logger.debug(f"Assessing tags for domain-doc {domainData['_id']}")

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

    for tag in domainData['_source']['sample_tags']:
        tagClass = tag['tag_class']
        tagName = tag['tag_name']

        app.logger.debug(f"Working on tag {tagName} with class of {tagClass}")
        
        if tagClass == "campaign":
            tagInfo = setDnsTagInfo(tag)
            tagInfo['confidence_level'] = 90
            taggedEvent = True
            app.logger.debug(f"Tag info set for {docID}: {json.dumps(tagInfo)}")
            break   # This the grand daddy of all tags 
                    # No need to keep processing the rest
            
        elif tagClass == "actor":
            tagInfo = setDnsTagInfo(tag)
            tagInfo['confidence_level'] = 90
            taggedEvent = True
            app.logger.debug(f"Tag info set for {docID}: {json.dumps(tagInfo)}")


        elif (tagClass == "malware_family") and not taggedEvent:
            tagInfo = setDnsTagInfo(tag)
            tagDate = tagInfo['date']
            
            # Figure out the confidence level for the malware based on how 
            # many days old it is. 
            tagAgeInDays = calcTimeDiff(getNow(),tagDate)
            
            if tagAgeInDays in tagConfLevels.keys():
                tagInfo['confidence_level'] = tagConfLevels[tagAgeInDays]
                app.logger.debug(f"confidence_level for " +
                                 f"{tagInfo['name']} @ date " +
                                 f"{tagInfo['date']}: "+
                                 f"{tagInfo['confidence_level']} based on" +
                                 f" age of {tagAgeInDays}")
            else:
                tagInfo['confidence_level'] = 5
                app.logger.debug(f"confidence_level for " +
                                 f"{tagInfo['name']} @ date " +
                                 f"{tagInfo['date']}: "+
                                 f"{tagInfo['confidence_level']} based on" +
                                 f" age of {tagAgeInDays}")
            taggedEvent = True
            app.logger.debug(f"Tag info set for {domainData['_id']}: {tagInfo}")

    # Went through all the tags available and none were of interest    
    if not taggedEvent:    
        tagInfo = dict.fromkeys(['public_name','name','class','date',"confidence_level"])
        tagInfo['public_name'] = "Not Available"
        tagInfo['name'] = "Not Available"
        tagInfo['class'] = "Not Available"
        tagInfo['date'] = "00-00-00T00:00:00:00Z"
        

    return tagInfo  


def main():
    pass


if __name__ == "__main__":
    main()
    