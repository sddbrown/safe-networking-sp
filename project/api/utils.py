#import os
import sys
import json
import time
import datetime
import requests
from elasticsearch import TransportError, RequestError, ElasticsearchException
#import autofocus
#import pan.afapi
#from __future__ import print_function


def calcCacheTimeout(cacheTimeout,lastDate,app):
    '''
    Calculate the time difference between two formatted date strings
    '''
    now = datetime.datetime.now()
    lastUpdatedDate = datetime.datetime.strptime(lastDate, '%Y-%m-%dT%H:%M:%SZ')
    calcDate = abs((now - lastUpdatedDate).days) 

    if calcDate < cacheTimeout:
        app.logger.debug(f"The calculated time is {calcDate} days vs setting of {cacheTimeout} days and should be good")
        return True
    else:
        app.logger.debug(f"The calculated time is {calcDate} days vs setting of {cacheTimeout} and needs to be updated")
        return False


def getDomainInfo(threatDomain,apiKey,app):
    '''
    Method that uses user supplied api key (instance/.panrc) and gets back a 
    "cookie."  Loops through timer (in minutes - set in instance/.panrc) and
    checks both the timer value and the maximum search result percentage and 
    returns the gathered domain data when either of those values are triggered
    '''
    searchURL = app.config["AUTOFOCUS_SEARCH_URL"]
    resultURL = app.config["AUTOFOCUS_RESULTS_URL"]
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
    resultData = {"apiKey": apiKey}
    headers = {"Content-Type": "application/json"}
    
    # Query AF and it returns a "cookie" that we use to view the resutls of the 
    # search
    app.logger.debug(f'Gathering domain info for {threatDomain}')
    queryResponse = requests.post(url=searchURL,headers=headers,data=json.dumps(searchData))
    queryData = queryResponse.json()
    cookie = queryData['af_cookie']
    cookieURL = resultURL + cookie
    app.logger.debug(f'Cookie {cookie} returned on query for {threatDomain} using {cookieURL}')

    # Wait for the alloted time before querying AF for search results.  Do check
    # every minute anyway, in case the search completed as the cookie is only valid
    # for 2 minutes after it completes. 
    for timer in range(app.config["AF_LOOKUP_TIMEOUT"]):
        time.sleep(60)
        cookieResults = requests.post(url=cookieURL,headers=headers,data=json.dumps(resultData))
        domainData = cookieResults.json()
        if domainData['af_complete_percentage'] >= app.config["AF_LOOKUP_MAX_PERCENTAGE"]:
            break
        else:
            app.logger.info(f"Search completion {domainData['af_complete_percentage']}% for {threatDomain} at {timer} minute(s)")

    
    return domainData


def updateDetailsDomainDoc(domainDoc,threatDomain,app):
    '''
    Method used to update the sfn-details document (dns-doc type) in ES so that 
    we have a "cached" version of the domain details and we don't have to go to 
    AF all the time
    calls getDomainInfo()
    '''

    # Set the doc's processed flag to 17 meaning we at least try it 
    try:
        app.es.update(index='sfn-details',doc_type='doc',id=domainDoc,
                    body={"domain-doc": {"processed": 17}})
    except TransportError as te:
        app.logger.error(f'Unable to communicate with ES server -{te.info}')
        return retStatusFail
    except RequestError as re:
        app.logger.error(f'Unable to update {docID} - {re.info}')
        return retStatusFail

    # call getDomainInfo() and if successful, parse out the info, replace the 
    # current data and update the last_updated value to now
    try:
        apiKey = app.config['AUTOFOCUS_API_KEY']
        hostname = app.config['AUTOFOCUS_HOSTNAME']

    
        app.logger.debug(f"Query to obtain gather domain info for {threatDomain}")
        domainDetails = getDomainInfo(threatDomain,apiKey,app)
        print(f'\n\n\n\n {domainDetails}\n\n\n\n')



#         afOutput = getTags(hostname, apiKey, 'get_tags', threatDomain, False, app)
#         print(f'{afOutput}')
#         return 1
#         # Conver

#         domain_dict = json.loads(af_output)

#         for item in domain_dict['hits']:
#             record = item['_source']
#             for item in record:

# # parsing the response to find the tag information
# # then when required, creating a new tag dictionary entry for newly found tags

#                 if 'tag' in record:
#                     af_tags = record['tag']
#                     for item in af_tags:
#                         if item in tag_dict:
#                             pass
#                         else:

#     # for new tags do a secondary query to get the tag type aka the 'tag class' in Autofocus
#     # this captures all tag responses in the local tag dictionary

#                             tag_types = getTags(hostname, api_key, 'tag_info', False, item,app)
#                             tags_dict = json.loads(tag_types)
#                             tag_dict[item] = {}
#                             tag_dict[item]['class'] = tags_dict['tag']['tag_class']


#                             if not tags_dict['tag_groups']:
#                                 pass
#                             else:                      
#                                 tag_dict[item]['group'] = tags_dict['tag_groups'][0]['tag_group_name']

#                                 # Append tag file with new tag data
#                             with open('tag_data.txt','w') as tagFile:
#                                 tagFile.write(json.dumps(tag_dict, indent=4, sort_keys=True))

#     # the application is looking for tags related to a named malware family
#     # If a match then the domain list dictionary is updated with the malware family
                        
#                         if tag_dict[item]['class'] == 'malware_family':
#                           if item in domains_and_tags[dns_domain]['malware']:
#                               pass
#                           else:
#                             domains_and_tags[dns_domain]['malware'].append(item)
# ##
#         print('\n' + json.dumps(domains_and_tags[dns_domain], indent=4))


        
        return True
    except KeyError as error:
        print(f"Unable to retrieve AutoFocus API key, verify it is set in instance/.panrc")
        app.logger.error(f"Unable to retrieve AutoFocus API key. Returned {error} when getting domain info for {threatDomain}")
        raise 
    


# # def getTags(hostname, api_key, action, domain, af_tag, app):


#     options = {
#         'sessions': False,
#         'aggregate': False,
#         'histogram': False,
#         'session': None,
#         'samples': False,
#         'sample_analysis': False,
#         'top_tags': False,
#         'tags': False,
#         'tag': None,
#         'export': False,
#         'json_requests': [],
#         'json_request': None,
#         'json_request_obj': None,
#         'num_results': None,
#         'scope': None,
#         'hash': None,
#         'terminal': False,
#         'api_key': api_key,
#         'api_version': None,
#         'hostname': hostname,
#         'ssl': False,
#         'print_python': False,
#         'print_json': True,
#         'debug': 0,
#         'panrc_tag': None,
#         'timeout': None,
#         }

#     print(f"In getTags with option of {af_tag} and apiKey of {api_key}")
#     if action == 'get_tags':

#         options['samples'] = True
#         lastYear = int(time.strftime("%Y")) - 1
#         query_arg = '{{"query":{{"operator":"all","children":[{{"field":"alias.domain","operator":"contains","value":"{0}"}},{{"field":"sample.tag_class","operator":"is in the list","value":["malware_family"]}}]}},"scope":"global","size":10,"from":0,"sort":{{"create_date":{{"order":"desc"}}}}}}'.format(domain)

#         options['json_requests'].append(process_arg(query_arg,app))

#         if options['json_requests']:
#             obj = {}
            
#             for r in options['json_requests']:
#                 try:
#                     x = json.loads(r)
#                 except ValueError as e:
#                     print('%s: %s' % (e, r), file=sys.stderr)
#                     sys.exit(1)
#                 obj.update(x)

#             try:
#                 options['json_request'] = json.dumps(obj)
#                 options['json_request_obj'] = obj
#             except ValueError as e:
#                 print(e, file=sys.stderr)
#                 sys.exit(1)


#     if action == 'tag_info':
#         options['tag'] = af_tag
        

#     try:
#         afapi = pan.afapi.PanAFapi(panrc_tag=options['panrc_tag'],
#                                    api_key=options['api_key'],
#                                    api_version=options['api_version'],
#                                    hostname=options['hostname'],
#                                    timeout=options['timeout'],
#                                    verify_cert=options['ssl'])

#     except pan.afapi.PanAFapiError as e:
#         print('pan.afapi.PanAFapi:', e, file=sys.stderr)
#         sys.exit(1)

#     if options['json_request'] is None:
#         options['json_request'] = '{}'
#         options['json_request_obj'] = {}

#     if options['samples']:
#         af_output = search_results(afapi, options,
#                        afapi.samples_search_results)
        

#     elif options['tag'] is not None:
#         af_output = tag(afapi, options)

#     return af_output

# def tag(afapi, options):
#     try:
#         action = 'tag'
#         r = afapi.tag(tagname=options['tag'])
#         print_status(action, r)
#         af_output = print_response(r, options)
#         exit_for_http_status(r)
#         return af_output

#     except pan.afapi.PanAFapiError as e:
#         print_exception(action, e)
#         sys.exit(1)


# def search_results(afapi,
#                    options,
#                    search):
#     request = options['json_request']

#     if options['num_results'] is not None:
#         try:
#             obj = json.loads(request)
#             obj['size'] = options['num_results']
#             request = json.dumps(obj)
#         except ValueError as e:
#             print(e, file=sys.stderr)
#             sys.exit(1)

#     if options['scope'] is not None:
#         try:
#             obj = json.loads(request)
#             obj['scope'] = options['scope']
#             request = json.dumps(obj)
#         except ValueError as e:
#             print(e, file=sys.stderr)
#             sys.exit(1)

#     try:
#         debug = 2
#         for r in search(data=request, terminal=options['terminal']):
#             print_status(r.name, r)
#             if debug > 2:
#                 af_output = print_response(r, options)
#         if debug <= 2:
#             af_output = print_response(r, options)

#     except pan.afapi.PanAFapiError as e:
#         print_exception(search.__name__, e)
#         sys.exit(1)
#     return af_output

# def print_exception(action, e):
#     print('%s:' % action, end='', file=sys.stderr)
#     print(' "%s"' % e, file=sys.stderr)


# def print_status(action, r):
#     print('%s:' % action, end='', file=sys.stderr)

#     if r.http_code is not None:
#         print(' %s' % r.http_code, end='', file=sys.stderr)
#     if r.http_reason is not None:
#         print(' %s' % r.http_reason, end='', file=sys.stderr)

#     if r.http_headers is not None:
#         # XXX
#         content_type = r.http_headers.get('content-type')
#         if False and content_type is not None:
#             print(' %s' % content_type, end='', file=sys.stderr)
#         length = r.http_headers.get('content-length')
#         if length is not None:
#             print(' %s' % length, end='', file=sys.stderr)

#     if r.json is not None:
#         if 'message' in r.json:
#             print(' "%s"' % r.json['message'],
#                   end='', file=sys.stderr)

#         if 'af_complete_percentage' in r.json:
#             print(' %s%%' % r.json['af_complete_percentage'],
#                   end='', file=sys.stderr)

#         if 'hits' in r.json:
#             hits = len(r.json['hits'])
#             print(' hits=%d' % hits, end='', file=sys.stderr)
#         elif 'tags' in r.json:
#             print(' tags=%d' % len(r.json['tags']),
#                   end='', file=sys.stderr)
#         elif 'top_tags' in r.json:
#             print(' top_tags=%d' % len(r.json['top_tags']),
#                   end='', file=sys.stderr)
#         elif 'export_list' in r.json:
#             print(' export_list=%d' % len(r.json['export_list']),
#                   end='', file=sys.stderr)

#         if 'total' in r.json:
#             print(' total=%d' % r.json['total'],
#                   end='', file=sys.stderr)
#         elif 'total_count' in r.json:
#             print(' total_count=%d' % r.json['total_count'],
#                   end='', file=sys.stderr)

#         if 'took' in r.json and r.json['took'] is not None:
#             d = datetime.timedelta(milliseconds=r.json['took'])
#             print(' time=%s' % str(d)[:-3],
#                   end='', file=sys.stderr)

#         if 'af_message' in r.json:
#             print(' "%s"' % r.json['af_message'],
#                   end='', file=sys.stderr)

#     print(file=sys.stderr)


# def print_response(r, options):
#     if r.http_text is None:
#         return

#     if r.http_headers is not None:
#         x = r.http_headers.get('content-type')
#         if x is None:
#             return

#     if x.startswith('text/html'):
#         ## XXX
#  #       print(r.http_text)
#         print()


#     elif x.startswith('application/json'):
#         if options['print_json']:
#             af_output = print_json(r.http_text, isjson=True)
#             return af_output

#         if options['print_python']:
#             print_python(r.http_text, isjson=True)


# def exit_for_http_status(r):
#     if r.http_code is not None:
#         if not (200 <= r.http_code < 300):
#             sys.exit(1)
#         else:
#             return
#     sys.exit(1)


# def print_json(obj, isjson=False):
#     if isjson:
#         try:
#             obj = json.loads(obj)
#         except ValueError as e:
#             print(e, file=sys.stderr)
#             print(obj, file=sys.stderr)
#             sys.exit(1)

#  #   print(json.dumps(obj, sort_keys=True, indent=4,
#  #                    separators=(',', ': ')))

#     af_output = json.dumps(obj, sort_keys=True, indent=4,
#                      separators=(',', ': '))

#     return af_output


# def process_arg(s, app, list=False):
#     stdin_char = '-'

#     if s == stdin_char:
#         lines = sys.stdin.readlines()
#     else:
#         try:
#             f = open(s)
#             lines = f.readlines()
#             f.close()
#         except IOError:
#             lines = [s]

#     app.logger.debug(f'lines: {lines}')

#     if list:
#         l = [x.rstrip('\r\n') for x in lines]
#         return l

#     lines = ''.join(lines)
#     return lines

def main():
    pass

if __name__ == "__main__":
    main()
    