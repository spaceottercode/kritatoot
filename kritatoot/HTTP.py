
import re
import sys

if sys.version_info < (3,):
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer #py2
else:
    from http.server import BaseHTTPRequestHandler, HTTPServer




    
class KritaTootHTTPServer(HTTPServer): # py2
    """
    sole purpose is to receive OAUTH 2 authorization code. see HTTPHandler class below.
    
    If server receives an auth code, getAuthCode() returns it
    
    If the server is cancelled, getCancelled( ) returns True
    
    If an error has occurred, getError() returns a tuple
    
    If no further requests remain, getEOF() returns True
    """

    def __init__(self, url, handler):
        HTTPServer.__init__(self, url, handler)
        
        # time server started. used to control servers duration time
        self.started = None
        
        
        # the OAuth code we are waiting for
        self.authcode = None
        
        self.cancelled = False
        
        # if an error occurs, no auth code, or timeout
        self.error     = False
        self.errcode   = 0
        self.errormsg  = ''
        
        # when True, no futher network I/O
        self.eof = False
        
        
    
    def hasCode(self):
        """
        Has server received/spotted an authorization code in a GET request
        """
        if self.code:
            return True
        else:
            return False
    
    
    def setAuthCode(self, value):
        self.authcode = value

    def getAuthCode(self):
        """
        Return the authorization code (a hexadecimal string) if server has spotted one, otherwise returns None
        """
        return self.authcode
    
    def setCancelled(self):
        self.cancelled = True

    def getCancelled(self):
        """
        Returns True if server was cancelled, otherwise returns False
        """
        return self.cancelled
    
    def setError(self, errcode, errormsg):
        self.error = True
        self.errcode = errcode
        self.errormsg = errormsg

    def getError(self):
        """
        Returns a tuple: (err_code, error_message) or None if no error
            err_code    (int) Arbitrary number. currently assigned numbers resembling http status codes
            err_message (str)
        
        The following error codes are implem
        
            204 - A /callback request-URI was received that neither contained a code param or
                  an error/error_description params.
            403 - The user or server denied your request to authorize app
            
        """
        
        if not self.error:
            return None
        
        return (self.errcode, self.errormsg)
    
    def setEOF(self):
        self.eof = True

    def getEOF(self):
        """
        Returns True if no further requests need handling (ie remain)
        """
        return self.eof
    



class HTTPHandler(BaseHTTPRequestHandler):
    """
    Responsible for processing GET requests.
    
    This handler is responsible for processing request-URIs beginning in:
    
        /cancel
        
            If the request-URI begins in /cancel, the handler informs the 
            KritaTootHTTPServer server to not expect additional requests (sets the server's EOF)
            and that it was cancelled (sets server's cancelled)
        
        
        /callback
    
            If the request-URI begins in /callback, the handler parses the remaining URI for a
            query string containing a code parameter or a error/error_description parameter-pairs.
            If the code param is found, the handler shares it with KritaTootHTTPServer server
            an informs the server not to expect additional requests (sets the server's EOF)
            
            If the error params are found or neither code or error params are found, the handler
            informs the KritaTootHTTPServer server of the error (error code and error message)
            
            If the remaining part of this request URI is non-comforming, an error is also set
    
    
    
    """


    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        print(self.path)

        if re.match('/callback', self.path):
            
            print('Terminating...')
            
            
            
            # path will ~= /callback?code=....
            # or /callback?error=access_denied&error_description=The+resource+owner+or+authorization+server+denied+the+request.
            
            matches = re.search('code=([a-f0-9]+)', self.path)
            
            if matches:
                
                self.wfile.write("<html><body><h2>KritaToot is now ready to post</h2></body></html>".encode('utf-8'))
                
                authcode = matches.groups()[0]
                self.server.setAuthCode(authcode)
                self.server.setEOF()
                return
            
            
            if re.search('error=', self.path):
                # rejected
                
                self.wfile.write("<html><body><h2>The resource owner or sever denied request</h2></body></html>".encode('utf-8'))
                
                self.server.setError(403, 'The resource owner or sever denied request')
                self.server.setEOF()
                return
            
            
            self.wfile.write("<html><body><h2>Failed to find authorization code in GET request</h2></body></html>".encode('utf-8'))
            self.server.setError(204, 'Failed to find authorization code in GET request')
            self.server.setEOF()
            
            
        elif re.match('/cancel', self.path):
            
            print('cancelled...')
            self.wfile.write("<html><body><h2>Cancelled</h2></body></html>".encode('utf-8'))
            self.server.setCancelled()
            self.server.setEOF()
            
        else:
            self.wfile.write("<html><body><h1>KritaToot: Awaiting OAuth authorization code</h1></body></html>".encode('utf-8'))


if __name__ == '__main__':
    
    
    server = KritaTootHTTPServer(('', 3000), HTTPHandler)
    
    for x in range(4):
        server.handle_request()
    
    server.server_close()
    