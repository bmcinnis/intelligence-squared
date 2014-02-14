## Intelligence Squared US (I2US) - Improve Data (Socket Server)
## Brian McInnis, Cornell University 2014

import imp

mods = ['os','pprint','pickle','re','json','urlparse','SimpleHTTPServer','SocketServer','sys','threading','BaseHTTPServer']
error = []
for m in mods:        
    try:
        imp.find_module(m)
    except:
        error.append(m)

if (len(error)>0):
    print """
---Please Install the following modules:
%s

*   I highly recommend installing the Python 'setuptools'
*       GO TO: (https://pypi.python.org/pypi/setuptools)
*   and then installing each module from the command line:
*       pip install <module>

""" %(",".join(error))
else:
    import os, pprint, pickle, re, sys, json

    import threading
    import BaseHTTPServer
    import SimpleHTTPServer
    import SocketServer

    from urlparse import urlparse, parse_qs

    if len(sys.argv) > 2:
        PORT = int(sys.argv[2])
        I = sys.argv[1]
    elif len(sys.argv) > 1:
        PORT = int(sys.argv[1])
        I = ""
    else:
        PORT = 5000
        I = ""


    debatePattern = ".*\.[p]$"
    debateDir = "i2Debates/"

    class i2ModifyDataHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/index.html'
            elif (re.match('.*[?].*',self.path)!=None):
                pprint.pprint(parse_qs(urlparse(self.path).query))
                self.path = '/index.html'
            return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

        def do_POST(self):
            """Handle a post request by returning the square of the number."""
            length = int(self.headers.getheader('content-length'))        

            data_string = self.rfile.read(length)
            jdata = json.loads(data_string)
            
            if ('action' in jdata):

                print 'Action in JDATA'
                if (jdata['action'] == 'reload-debates'):

                    print 'Action in JDATA == RELOAD-DEBATES'                    
                    debateFiles = os.listdir(debateDir)
                    debateFiles = [d for d in debateFiles if re.match(debatePattern,d)]
                    pprint.pprint(debateFiles);
                    data_string = json.dumps({'debate-list':debateFiles})
                elif (jdata['action'] == 'retrieve-debates'):

                    if ('data' in jdata):
                        debateFiles = os.listdir(debateDir)

                        if(jdata['data'] in debateFiles):
                            dF = pickle.load(open(r'%s/%s' %(debateDir,jdata['data']),'rb'));
                            pprint.pprint(dF.keys())
                            data_string = json.dumps({'debate-file':jdata['data'],
                                                      'debate-content':dF})
                            
            self.wfile.write(data_string)
            
    def start_server():
        """Start the server."""
        server_address = ("", PORT)
        print "Serving at: http://%(interface)s:%(port)s" % dict(interface=I or "localhost", port=PORT)
        server = BaseHTTPServer.HTTPServer(server_address, i2ModifyDataHandler)
        server.serve_forever()

    if __name__ == "__main__":
        start_server()
