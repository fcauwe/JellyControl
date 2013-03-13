#!/usr/bin/env python

# (C) 2011 Francois Cauwe
# This code can be freely distributed under the terms of the LGPL License.


#Load Global library's
import logging
import string,cgi,time
from time import gmtime, strftime
import os, os.path
import BaseHTTPServer
import base64,json
## Redefine address lookup function, to avoid crazy delays
def not_insane_address_string(self):
    host, port = self.client_address[:2]
    return '%s' % host #used to call: socket.getfqdn(host)
BaseHTTPServer.BaseHTTPRequestHandler.address_string = not_insane_address_string
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

#Load Private library's
import GlobalObjects
import WebInterfaceJSON

class WebInterfaceHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if len(self.path) <4:
                filename = "index.html"
                args = {}
            elif (self.path.rfind("?")>0):
                filename=self.path[self.path.rindex("/")+1:self.path.rfind("?")]
                args_string=self.path[self.path.rindex("?")+1:]
                args = {}
                if  (self.path.rfind("=")>0):
                    for item in args_string.split('&'):
                        key,value = item.split('=')
                        args[ key ] =  value 
            else:
                filename=self.path[self.path.rindex("/")+1:]
                args = {}
                
            if not self.headers.has_key("Authorization"):
                self.send_response(401)
                self.send_header('Content-type','text/html')
                self.send_header('WWW-Authenticate', 'Basic realm="dotControl"')
                self.end_headers()
                self.wfile.write('Authentification required')
                return
            else:
                authentification = base64.b64decode(self.headers["Authorization"].split(" ")[1])
                username = authentification.split(":")[0]
                password = authentification.split(":")[1]
                if ((username!="tester") and (password!="12345")):
                    self.send_response(401)
                    self.send_header('Content-type','text/html')
                    self.send_header('WWW-Authenticate', 'Basic realm="dotControl"')
                    self.end_headers()
                    self.wfile.write('Authentification required')
                    return

            if filename.endswith(".html"):
                f = open(os.curdir + os.sep + "WebInterface" + os.sep + filename) 
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            if filename.endswith(".css"):
                f = open(os.curdir + os.sep + "WebInterface" + os.sep + "include" + os.sep + filename) 
                self.send_response(200)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            if filename.endswith(".png"):
                f = open(os.curdir + os.sep + "WebInterface" + os.sep + "include" + os.sep + filename,'rb') 
                self.send_response(200)
                self.send_header('Content-type','image/png')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            if filename.endswith(".ico"):
                f = open(os.curdir + os.sep + "WebInterface" + os.sep + "include" + os.sep + filename,'rb') 
                self.send_response(200)
                self.send_header('Content-type','image/x-icon')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            if filename.endswith(".js"):
                path_to_file = os.curdir + os.sep + "WebInterface" + os.sep + "include" + os.sep + filename
                if self.headers.has_key("If-None-Match"):
                  if (self.headers['If-None-Match']==str(os.path.getmtime(path_to_file))):
                    self.send_response(304)
                    self.send_header('Etag',os.path.getmtime(path_to_file))
                    return

                f = open(path_to_file)
                self.send_response(200)

                self.send_header('Content-type','application/x-javascript')
                self.send_header('Last-Modified',strftime("%a, %d %b %Y %H:%M:%S GMT",
                                                          gmtime(os.path.getmtime(path_to_file))))
                self.send_header('Etag',os.path.getmtime(path_to_file))
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            
            if filename.endswith(".json"):   #our dynamic content
                if not args.get( 'jsoncallback' ):
                    self.send_error(403,'Internal error: argument jsoncallback missing.')                     
                    return
                
                json_response = WebInterfaceJSON.Process(filename,args)

                self.send_response(200)
                #self.send_header('Content-type',	'application/json')
                self.send_header('Content-type',	'text/html')
                self.send_header('Cache-Control','no-cache')
                self.send_header('Pragma','no-cache')
                self.end_headers()
                self.wfile.write(str(args[ 'jsoncallback' ]) + ' ( \n')
                self.wfile.write(json.dumps(json_response))
                self.wfile.write('); \n')

                return

            
            self.send_error(404,'File Not Found 1: %s' % filename)                
            return
                
        except IOError:
            self.send_error(404,'File Not Found 2: %s' % filename)
     

    def do_POST(self):
        try:
            if len(self.path) <4:
                filename = "index.html"
                args = {}
            elif self.path.rfind("?")>0:
                filename=self.path[self.path.rindex("/")+1:self.path.rfind("?")]
                args_string=self.path[self.path.rindex("?")+1:]
                args = {}
                for item in args_string.split('&'):
                    key,value = item.split('=')
                    args[ key ] =  value 
            else:
                filename=self.path[self.path.rindex("/")+1:]
                args = {}

            # Import post headers
            length = int(self.headers.getheader('content-length'))        
            data_string = self.rfile.read(length)
            for item in data_string.split('&'):
                key,value = item.split('=')
                args[ key ] =  value 
            
            if filename.endswith(".json"):   #our dynamic content
                if not args.get( 'jsoncallback' ):
                    self.send_error(403,'Internal error: argument jsoncallback missing.')                     
                    return
                
                json_response = WebInterfaceJSON.Process(filename,args)

                self.send_response(200)
                #self.send_header('Content-type',	'application/json')
                self.send_header('Content-type',	'text/html')
                self.send_header('Cache-Control','no-cache')
                self.send_header('Pragma','no-cache')
                self.end_headers()
                self.wfile.write(str(args[ 'jsoncallback' ]) + ' ( \n')
                self.wfile.write(json.dumps(json_response))
                self.wfile.write('); \n')

                return

            self.send_error(404,'File Not Found 1: %s' % filename)                
            return
 


#        global rootnode
#        try:
#            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
#            if ctype == 'multipart/form-data':
#                query=cgi.parse_multipart(self.rfile, pdict)
#            self.send_response(301)
#            
#            self.end_headers()
#            upfilecontent = query.get('upfile')
#            print "filecontent", upfilecontent[0]
#            self.wfile.write("<HTML>POST OK.<BR><BR>");
#            self.wfile.write(upfilecontent[0]);
            
        except IOError:
            pass

    def log_message(self, format, *args):
        logger.info("%s - %s" % (self.address_string(), format%args))



class MultiThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    def finish_request(self, request, client_address):
        request.settimeout(60)
        # "super" can not be used because BaseServer is not created from object
        BaseHTTPServer.HTTPServer.finish_request(self, request, client_address)





def Launch():
    # Create logger
    global logger
    logger = logging.getLogger("WebInterface")
    try:
        server = MultiThreadedHTTPServer(('', int(GlobalObjects.config_webinterface['port'])), WebInterfaceHandler)
        logger.info("Started httpserver...")
        while (GlobalObjects.running):
            server.handle_request()
        
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        GlobalObjects.running=False
        server.socket.close()
