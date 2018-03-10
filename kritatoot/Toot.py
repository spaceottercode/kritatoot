
import os
import sys
import re
import json

if sys.version_info < (3,):
    from urllib import urlencode
    from urllib2 import urlopen, Request
    from urlparse import urljoin
else:
    from urllib.parse import urlencode, urljoin
    from urllib.request import urlopen, Request


def uploadmedia(url, access_token, filename):
    """
    url - e.g. https://example.com
    
    returns a media id (numeric string) if successful, otherwise returns None
    """
    # TODO gen rand 16 char hex string instead of using a fixed one
    
    # POST
    # file (req) (multipart/form-data)
    # description
    
    endpt = urljoin(url, '/api/v1/media')
    
    headers = {'Accept':'application/json', 'Authorization':'Bearer ' + access_token,
               'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0',
               'Content-Type': 'multipart/form-data; boundary=------------------------d74496d66958873e'}
    
    data_head = '''--------------------------d74496d66958873e
Content-Disposition: form-data; name="file"; filename="%s"
Content-Type: application/octet-stream

''' % os.path.basename(filename)
    
    data_head = re.sub('\n', '\r\n', data_head)
    
    data_head_utf8 = data_head.encode('utf-8')
    
    try:
        fd = open(filename, 'rb')
        imgdata = fd.read()
    except Exception:
        print('Failed to read "%s"' % filename)
        return None
    
    fd.close()
    
    data_tail = '''\r\n--------------------------d74496d66958873e--\r\n'''
    data_tail_utf8 = data_head.encode('utf-8')
    
    data_utf8 = data_head_utf8 + imgdata + data_tail_utf8
    
    headers['Content-Length'] = len(data_utf8)
    
    try:
        httpreq = Request(endpt, data=data_utf8, headers=headers)
        response = urlopen(httpreq)
    except Exception:
        print('urlopen in uploadmedia() encountered an error')
        return None
    
    statuscode = response.getcode()
    print(statuscode)
    
    if statuscode == 200:
        jsontext = response.read().decode('utf-8')
        jsondata = json.loads(jsontext)
    
        # returns an Attachment json (Mastodon API)
        try:
            print(jsontext)
        except:
            # harmless error
            pass
    
        return jsondata['id']
    else:
        print('Failed to upload media')
        return None
    
    



def postmedia(url, access_token, media_id, message=None, visibility='public', spoiler_text=None, sensitive=False):
    """
    media_id (string) cannot be re-used
    visibility: 'public', 'unlisted', 'private', 'direct'
    sensitive: True or False
    """
    
    # visibility must be one of the following: 'public', 'unlisted', 'private', 'direct'
    if visibility not in ['public', 'unlisted', 'private', 'direct']:
        visibility = 'public'
    
    # convert python bool into string repr
    sensitive = 'true' if sensitive else 'false'
    
    # POST
    # status (req)
    # visibility : public, unlisted, private, direct
    # media_ids, sensitive
    # spoiler_text
    # in_reply_to_id
    
    endpt = urljoin(url, '/api/v1/statuses')
    
    headers = {'Accept':'application/json', 'Authorization':'Bearer ' + access_token,
               'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'}
    
    
    params = {'visibility':visibility, 'sensitive':sensitive}
    
    # status param always required. value must be non-empty string
    params['status'] = 'posted with KritaToot'
    
    if message:
        params['status'] = message

        
    
    if spoiler_text:
        params['spoiler_text'] = spoiler_text
    
    
    data = urlencode(params)
    
    # arrays require a perculiar format: array[]=value1&array[]=value2...
    data += '&media_ids%5B%5D=' + media_id
    
    #print(data)
    
    try:
        data_utf8 = data.encode('utf-8')
        httpreq = Request(endpt, data=data_utf8, headers=headers)
        response = urlopen(httpreq)
    except Exception:
        print('urlopen in postmedia() encountered an error')
        return False
    
    statuscode = response.getcode()
    print(statuscode)
    
    if statuscode == 200:
        jsontext = response.read().decode('utf-8')
        jsondata = json.loads(jsontext)
        
        try:
            print(jsontext)
        except:
            # harmless error
            pass
        
        return True
        
    else:
        print('Failed to post media')
        return False


def post(url, access_token, message, visibility='public', spoiler_text=None):
    """
    POST-ing with URL-encoded data  (Content-Type: application/x-www-form-urlencoded)
    """
    
    if not message:
        print('Invalid message')
        return False
    
    # visibility must be one of the following: 'public', 'unlisted', 'private', 'direct'
    if visibility not in ['public', 'unlisted', 'private', 'direct']:
        visibility = 'public'
    
    
    # POST
    # status (req)
    # visibility : public, unlisted, private, direct
    # spoiler_text
    # media_ids, sensitive
    # in_reply_to_id
    
    endpt = urljoin(url, '/api/v1/statuses')
    
    headers = {'Accept':'application/json', 'Authorization':'Bearer ' + access_token,
               'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'}
    params = {'status':message, 'visibility':visibility}
    
    if spoiler_text:
        params['spoiler_text'] = spoiler_text
    
    data = urlencode(params)
    
    try:
        data_utf8 = data.encode('utf-8')
        httpreq = Request(endpt, data=data_utf8, headers=headers)
        response = urlopen(httpreq)
    except Exception:
        print('urlopen in post() encountered an error')
        return
    
    
    statuscode = response.getcode()
    print(statuscode)
    
    jsontext = response.read().decode('utf-8')
    jsondata = json.loads(jsontext)
    
    try:
        print(jsontext)
    except:
        pass
    
    
    
    


