#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import re
import os



class defaultRequestHandler(BaseHTTPRequestHandler):
	mimetype	= ""

	def FindMimeType(self):
		if self.path.endswith(".html"):
			self.mimetype='text/html'
		elif self.path.endswith(".jpg"):
			self.mimetype='image/jpg'
		elif self.path.endswith(".png"):
			self.mimetype='image/png'
		elif self.path.endswith(".gif"):
			self.mimetype='image/gif'
		elif self.path.endswith(".js"):
			self.mimetype='application/javascript'
		elif self.path.endswith(".css"):
			self.mimetype='text/css'
		else:
			return False
		return True
	
	def sendHeader200WithMimetype(self):
		self.send_response(200)
		self.send_header('Content-type',self.mimetype)
		self.end_headers()
		
	def sendRequestedFile(self):
		self.sendHeader200WithMimetype()
		print(curdir + self.path)
		f = open(curdir + self.path) 
		self.wfile.write(f.read())
		f.close()
		
	def sendWebFileRequest(self):
		if self.FindMimeType():
			self.sendRequestedFile()
			
	def sendDynamicWebFileRequest(self):
		print "default sendDynamicWebFileRequest"
		if re.match('dynamicwebpageexample.html',self.path):
			arg1 = "arg1example"
			arg2 = "arg2example"
			self.sendHeader200WithMimetype()
			f = open("/ZodiacScripts/HTML" + self.path)		
			self.wfile.write(f.read()  % (arg1 , arg2) )
			f.close()
		else:
			return False
		return True
			
	def FindCommand(self):
		if re.match('/rebootpi', self.path):
			os.system("reboot")				
		elif re.match('/gettime', self.path):
			os.system("/usr/sbin/ntpd -s")	
		else:
			return False
		return True
	

	def do_GET(self):
		if self.path == "/":
			self.path += "index.html"
		try:
			if self.FindCommand():
				self.path = "/index.html"				
			if self.sendDynamicWebFileRequest():
				return		
			self.sendWebFileRequest()
		
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)
			


class myWebServerClass():
	portnr 				= 8080
	theRequestHandler		= defaultRequestHandler

	def __init__(self, portnr, myRequestHandler ):
		self.portnr		= portnr
		self.theRequestHandler	= myRequestHandler
		
	def run(self):
		try:
			server = HTTPServer(('', self.portnr), self.theRequestHandler)
			print 'Started httpserver on port ' , self.portnr	
			server.serve_forever()

		except KeyboardInterrupt:
			print '^C received, shutting down the web server'
			server.socket.close()
		
		