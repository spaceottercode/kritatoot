
import os
import sys
import json
import threading

if sys.version_info < (3,):
    from urllib import urlencode
    from urllib2 import urlopen, Request
    from urlparse import urljoin
else:
    from urllib.parse import urlencode, urljoin
    from urllib.request import urlopen, Request


import webbrowser


from .HTTP import KritaTootHTTPServer, HTTPHandler

class KritaTootAccount:
    """
    Object representing registered accounts
    At the moment, these accounts are on a per url basis (one per mastodon url) and not user handle.
    
    Multiple accounts on the same url not supported in this release
    """
    
    def __init__(self, url, appid=None, client_id=None, client_secret=None, token_expiration=None, access_token=None, refresh_token=None):
        
        self.url = url
        
        # always use the getters/setters
        # the properties below are subject to change
        
        self.appid = appid
        
        self.client_id = client_id
        self.client_secret = client_secret
        
        self.token_expiration = token_expiration
        self.access_token = access_token
        self.refresh_token = refresh_token
        
        
    def setURL(self, url):
        
        self.url = url
    
    def getURL(self):
        
        return self.url
    
    def setAppID(self, appid):
        
        self.appid = appid
    
    def getAppID(self):
        
        return self.appid
    
    def setClientID(self, client_id):
        
        self.client_id = client_id
    
    def getClientID(self):
        
        return self.client_id
    
    def setClientSecret(self, client_secret):
        
        self.client_secret = client_secret
    
    def getClientSecret(self):
        
        return self.client_secret
    
    
    
    def setTokenExpiration(self, expiration):
        
        self.token_expiration = expiration
    
    def getTokenExpiration(self):
        
        return self.token_expiration
    
    def setAccessToken(self, access_token):
        
        self.access_token = access_token
    
    def getAccessToken(self):
        
        return self.access_token
    
    def setRefreshToken(self, refresh_token):
        
        self.refresh_token = refresh_token
    
    def getRefreshToken(self):
        
        return self.refresh_token








class KritaToot:
    """
    This object represents the bulk* of app's logic. The front-end is handle separately by the KritaTootUI object.
    
    (* a minimal amount of logic has been outsourced to Toot module)
    
    This object is responsible for:
    
        loading & saving accounts:
        
            loadAccounts(), saveAccounts()
            
        adding & removing & managing accounts:
        
            addAccount(), removeAccount(), getAccount(), ...
            
        running an http server in the background that sits and waits for a local GET request. See runHTTPServer( ) for details
            runHTTPServer(), stopHTTPServer()
        
        registering app on a given mastodon site
            register()
        
        launching web page hosted on the mastodon server where user must either authorize or deny app further access.
        Kritatoot only uses write access (scope) since there is no finer access/scope available. No other scopes are needed.
            authorize()
        
        fetching an access token (once authorized)
            requestToken()
    
    Functions for uploading and posting media reside in Toot.py module
    """
    
    def __init__(self):
        
        # information supplied to the registeration proc
        self.client_name = 'KritaToot'
        self.website = 'https://github.com/spaceottercode/kritatoot'
        
        # A minimal http server that runs in the bg when a authorization code
        # is expected.
        # The server runs in a separate thread
        # At most one web server can run
        self.httpd = None
        self.httpport = None
        
        # because signaling to a web browser to open a url doesnt always work in the first try
        # we hold on to the url with the needed params for a bit
        self.authurl = None
        
        # where the accounts are kept if storage type is 'file'
        self.appdir = os.path.join( os.path.expanduser('~'), '.kritatoot')
        self.acctfile = 'accounts'
        
        # for now, only one account is supported
        self.accounts = []
        
    
    def getStorageType(self):
        """
        encapsulated so that other storage methods can be added (e.g. keyring)
        """
        
        return 'file'
    
    def loadAccounts(self):
        """
        load accounts from file, keyring or other storage. atm only file storage is supported
        """
        
        accounts = []
        
        storage_type = self.getStorageType()
        
        url = None
        
        appid = None
        
        client_id     = None
        client_secret = None
        expiration    = None
        access_token  = None
        refresh_token = None
        
        
        if storage_type == 'file':
            filename = os.path.join(self.appdir, self.acctfile)
            
            dataform = None
            
            try:
                with open(filename, 'r') as acctfile:
                    content = acctfile.read()
                    dataform = json.loads(content)
                
            except Exception as e:
                print( e.args )
                print('accounts not found')
                return
                
            
            # extract the following (if any):  url, client_id, client_secret, token_expiration, access_token, refresh_token
            
            if dataform:
                for account in dataform['accounts']:
                    url = account.get('url')
                    
                    appid = account.get('appid')
                    
                    client_id     = account.get('client_id')
                    client_secret = account.get('client_secret')
                    expiration    = account.get('token_expiration')
                    access_token  = account.get('access_token')
                    refresh_token = account.get('refresh_token')
        
                    if url:
                        account = KritaTootAccount(url, appid=appid, client_id=client_id, client_secret=client_secret, token_expiration=expiration,
                                                           access_token=access_token, refresh_token=refresh_token)
                        
                        accounts.append(account)
        
        self.accounts = accounts
    
    
    def saveAccounts(self):
        """
        """
        
        storage_type = self.getStorageType()
        
        if storage_type == 'file':
            filename = os.path.join(self.appdir, self.acctfile)
            
            if not os.path.exists(self.appdir):
                os.mkdir(self.appdir)
            
            
            data = {'accounts':[]}
            
            for account in self.accounts:
                
                # only save accounts that have at least: url, appid, client_id, client_secret
                
                url = account.getURL()
                appid = account.getAppID()
                client_id = account.getClientID()
                client_secret = account.getClientSecret()
                
                expiration    = account.getTokenExpiration()
                access_token  = account.getAccessToken()
                refresh_token = account.getRefreshToken()
                
                if url and appid and client_id and client_secret:
                    data['accounts'].append({'url':url, 'appid':appid, 'client_id':client_id, 'client_secret':client_secret,
                                             'access_token':access_token, 'token_expiration':expiration, 'refresh_token':refresh_token})
            
            
            jsontext = json.dumps(data)
            
            
            try:
                # because we need to start off with a file that can only be read/write by the user only
                fd = os.open(filename, os.O_WRONLY | os.O_CREAT, 0o600)
                
                #with open(fd, 'w') as acctfile: # not backwards compat
                with os.fdopen(fd, 'w') as acctfile:
                    acctfile.write(jsontext)
                
                return True
                
            except Exception as e:
                print(e.message)
                print('Failed to save accounts')
                return False
    
    
    
    
    def getAccountsLength(self):
        """
        How many accounts
        """
        
        return len(self.accounts)
    
    
    def getAccountURLs(self):
        """
        """
        
        urls = []
        
        for account in self.accounts:
            url = account.getURL()
            urls.append(url)
        
        return urls
    
    def getAccount(self, url):
        """
        Return a matching KritaTootAccount object, or None if no match exists
        """
        
        for account in self.accounts:
            if account.getURL() == url:
                return account
        
        return None
    
    def addAccount(self, url, appid, client_id, client_secret):
        """
        Add a new account to app.
        
        Note: This call does not save accounts to storage. Use saveAccounts()
        """
        
        account = self.getAccount(url)
        
        if account:
            # update an existing account
            account.setAppID(appid)
            account.setClientID(client_id)
            account.setClientSecret(client_secret)
        else:
            # new account
            account = KritaTootAccount(url, appid=appid, client_id=client_id, client_secret=client_secret)
            
            self.accounts.append(account)
        
        return True
    
    
    def removeAccount(self, url):
        """
        Note - This call does not save accounts to storage. Use saveAccounts() to update storage.
        Note - Removing an account from the app does not remove it from the Mastodon site.
               There appears to be no REST API call for revoking/removing apps on the server
        """
        
        # accounts is a list of obj atm
        index = -1
        
        counter = 0
        
        for account in self.accounts:
            currurl = account.getURL()
            
            if currurl == url:
                index = counter
                break
            
            counter += 1
        
        if index >= 0:
            self.accounts.pop(index)
        
        
        
    
    
    
    def runHTTPServer(self, onready=None, onabort=None, onerror=None, port=3000):
        """
        
        onready - called only when the auth code was found in a GET request, otherwise onerror is invoked
        
            args:
                    authcode (str) hex string or rarely None
        
        onabort - called when operation was cancelled
        
        onerror - called when operation failed or encounter an error
                
            args:
                    error code (int)
                    message (str)
        
        
        runHTTPServer runs a proc in the bg (in a separate thread)
        and waits for the browser to construct a GET request, 
        with the needed authorization code. See the HTTPHandler in HTPP.py
        
        By default the server runs on port 3000.
        
        You can access the server on http://localhost:3000
        
        Two particular request-URIs in the GET request trigger the server:
        
            /cancel
            /callback....
        
        The /cancel path causes the server to terminate
        
        The /callback... path causes the server to scour the rest of the path for
        parameters. A 'code' parameter for an authorization code or the request.
        
        See HTTPHandler in HTTP module
        
        
        When the server teminates, it invokes one of the callbacks above, if any.
        
        The server runs async/thread
        
        The callbacks run in a separate thread as well. Note, some QT calls can
        only be made in the original thread
        
        
        Server terminates when:
            * receives an explicit call to terminate with stopHTTPServer()
            * it receives one of the two awaited GET request
            * user denies authorization
            * times out (not implem)
            
        
        
        Note: Only one active http server is allowed at a time.
        """
        
        if self.httpd:
            print('Server already running')
            #self.stopHTTPServer()
            return
        
        
        serverurl = ('', port)
        httpd = KritaTootHTTPServer(serverurl, HTTPHandler)
        
        self.httpd = httpd
        self.httpport = port
        
        def runserver():
            print('Running HTTPd server')
            
            # TODO check how long server has been running
            # and cease looping if too long
            
            while not httpd.getEOF():
                httpd.handle_request()
            
            # three callbacks are currently supported:
            # onready, onerror, and onabort (see doc string)
            
            # cancelled?
            if httpd.getCancelled():
                
                if onabort:
                    onabort()
            
            # succeeded?
            elif httpd.getAuthCode():
                
                if onready:
                    
                    authcode = httpd.getAuthCode()
                    onready(authcode)
            
            # failed or error
            else:
                
                # else we have an error or failure
                error = httpd.getError()
                
                if onerror:
                    
                    if error:
                        onerror(error[0], error[1])
                    else:
                        onerror(418, 'Unknown Error')
            
            
            httpd.server_close()
            
            self.httpd    = None
            self.httpport = None
        
        
        # dont stall main thread; run on a separate thread
        server_thread = threading.Thread(target=runserver)
        server_thread.daemon = False
        server_thread.start()
        
    
    def stopHTTPServer(self):
        """
        stops the http server, if present. otherwise does nothing
        """
        
        if self.httpd:
            
            # redundant
            self.httpd.setCancelled() 
            self.httpd.setEOF()
            
            urlopen('http://localhost:%i/cancel' % self.httpport) # py2
            # let the runserver proc handle the rest of the shutdown
    
    
    def register(self, url):
        """
        Register app on Mastodon site. If successful Mastodon site will issue the following:
        
            unique app ID    (numeric string)
            
            unique client ID (hexadecimal string) (part of OAuth2 spec)
            
            a secret hexadecimal string, called the client secret, the app must use to request access tokens
            that may or may not expire (part of OAuth2 spec)
            
        These are needed for many other server requests.
        """
        
        # returns an obj with the following properties
        #
        #   id
        #   name
        #   website
        #   redirect_uri
        #   client_id
        #   client_secret
        #
        
        endpt = urljoin(url, '/api/v1/apps')
        
        headers = {'Accept':'application/json', 'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'}
        
        data = urlencode({'client_name': self.client_name, 'scopes':'write', 'redirect_uris':'http://localhost:3000/callback', 'website':self.website})
        
        data_utf8 = data.encode('utf-8')
        httpreq = Request(endpt, data=data_utf8, headers=headers)
        
        try:
            response = urlopen(httpreq)
        except Exception as e:
            print('urlopen in register() encountered an error')
            return False
        
        jsondata = {}
        
        statuscode = response.getcode()
        print(statuscode)
            
        if statuscode == 200:
            jsontext = response.read().decode('utf-8')
            jsondata = json.loads(jsontext)
            
            #print(jsontext)
            
            
            appid         = jsondata.get('id')
            client_id     = jsondata.get('client_id')
            client_secret = jsondata.get('client_secret')
            
            self.addAccount(url, appid, client_id, client_secret)
            
            
            
            return True
            
        else:
            print('Failed to register app')
            return False
    
    
    def setAuthURL(self, authurl):
        self.authurl = authurl
        
    def getAuthURL(self):
        """
        Returns the URL the user needs to visit in order to authorize (or deny) the app access to the Mastodon site being visited
        """
        return self.authurl
    
    def authorize(self, url):
        """
        Given a previously acquired client ID (see register() call), launch a web page hosted on the Mastodon user's site
        where the user can authorize (or deny) your app access. If user is not signed in, user is asked to sign in before
        the authorization page appears. User must access site thru this web url.
        
        Note - webbrowser call is responsible for opening the authorization URL in the user's default web browser but sometimes fails to do so.
        You can fetch this URL with getAuthURL() call.
        
        This call instructs the Mastodon site to respond using a local GET request (supplying a URL callback) (see OAuth spec). As a result you must
        run a server capable of receiving HTTP GET requests locally (use runHTTPServer( ) call). The GET request-URI will begin with /callback followed
        by a query string containing the following URL parameter(s):
        
            code=<HEXSTRING>
        
        or,
        
            error=<STRING>
            error_description=<STRING>
        
        
        For example:
        
            /callback?code=feedadeadd0d0c0ffee
        
        code is the authorization code needed to request an access token. If the user or Mastodon site rejects your request, an error and error_description will
        be supplied.
        
        URL callback must match the one used during registration.
        
        Note - app must have a client id
        """
        
        account = self.getAccount(url)
        
        if not account:
            print('An account must be registered before it can be authorized')
            return False
        
        client_id = account.getClientID()
        
        if not client_id:
            print('Invalid client id')
            return False
        
        endpt = urljoin(url, '/oauth/authorize')
    
        data = urlencode({'client_id': client_id, 'scope':'write', 'redirect_uri':'http://localhost:3000/callback', 'response_type':'code'})
    
        #print( endpt + '?' + data)
        
        self.setAuthURL(endpt + '?' + data)
        
        webbrowser.open_new(endpt + '?' + data)
        
        return True
    


    def requestToken(self, url, auth_code):
        """
        Given an authorization code an access token from the Mastodon site is requested. App must be registered (have a client id and secret id)
        and authorized (have an authorization code).
        
        URL callback must match the one used during registration and authorization. Some sites require a known user-agent.
        
        Call returns the following:
        
            access token (hexadecimal string). This should aslo be kept secret.
            
            time token was created (numeric string) unix epoch?
            
            token type (string) always "bearer"
            
            requested scope(s) this token was granted (string)
            
        Only access token is saved atm
        
        Note - No refresh token or token expiration is returned
        """
        
        account = self.getAccount(url)
        
        if not account:
            print('An account must be registered before a token can be granted')
            return False
        
        client_id = account.getClientID()
        
        if not client_id:
            print('Invalid client id')
            return False
        
        client_secret = account.getClientSecret()
        
        if not client_secret:
            print('Invalid client data')
            return False
        
        # POST
        # client_id
        # client_secret
        # redirect_uri
        # grant_type = 'authorization_code'
        # code
    
        endpt = urljoin(url, '/oauth/token')
        
        
        data = urlencode({'client_id': client_id, 'client_secret':client_secret, 'redirect_uri':'http://localhost:3000/callback',
                                'grant_type':'authorization_code', 'code':auth_code})
        
        
        # user agent required
        headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'}
        
        data_utf8 = data.encode('utf-8')
        httpreq = Request(endpt, data=data_utf8, headers=headers)
        
        #{"access_token":"...","token_type":"bearer","scope":"write","created_at":1519931763}
        
        
        try:
            response = urlopen(httpreq)
        except Exception as e:
            print('urlopen in requestToken encountered an error')
            return False
        
        jsondata = {}
        
        statuscode = response.getcode()
        print(statuscode)
            
        if statuscode == 200:
            jsontext = response.read().decode('utf-8')
            jsondata = json.loads(jsontext)
            
            #print(jsontext)
            
            
            access_token  = jsondata.get('access_token')
            #expiration    = jsondata.get('expires_in')
            #refresh_token = jsondata.get('refresh_token')
            
            account.setAccessToken(access_token)
            
            self.saveAccounts()
            
            return True
            
        else:
            print('Failed to fetch token')
            return False




if __name__ == '__main__':
    
    app = App.KritaToot()
    
    
    def onready(code): print(code)
    
    def onabort(): print('server cancelled')
    def onerror(code, message): print(message)
    
    app.runHTTPServer(onready=onready, onabort=onabort, onerror=onerror)
    
    url = 'https://mastodon.social'
    app.register(url)
    app.authorize(url)
    
    authurl = app.getAuthURL()
    webbrowser.open_new(authurl)
    
    authcode = ''
    #app.requestToken(url, authcode)
    
    app.getAccountsLength()
    
    app.saveAccounts()
    
    app.accounts = []
    app.getAccountsLength()
    
    app.loadAccounts()
    app.getAccountsLength()
    
    

