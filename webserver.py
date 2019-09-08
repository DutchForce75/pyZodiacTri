#!/usr/bin/env python
# coding=utf-8

from myZodiacTriClass import *
from myWebServerClass import *
import time
import resource
from threading import Thread,Event

RS485Device = "/dev/ttyUSB0"

class MyThread(Thread):
	def __init__(self, event, zodiacTriClass):
		myzodiac = zodiacTriClass
		Thread.__init__(self)
		self.daemon = True
		self.stopped = event

	def run(self):
		while not self.stopped.wait(5):
			if myzodiac.active:
				myzodiac.sendCmdProbe()
				myzodiac.readMsg()
				myzodiac.sendCmdSetPercentage()
				myzodiac.readMsg()


class myRequestHandler( defaultRequestHandler ):
	myzodiac=0
	def setzodiac(self,zodiacTriClass):
		self.myzodiac = zodiacTriClass
		
	def SendIndex(self):			
		arg1 = time.asctime( time.localtime(time.time()))
		arg9 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
		if self.myzodiac.connected:	
			arg2 = "checked" if (self.myzodiac.active) else ""
			arg3 = str(self.myzodiac.chloricpct) 
			if (self.myzodiac.chloricpct==101):	arg4 = "boost"
			elif (self.myzodiac.chloricpct==0):	arg4 = "off"
			else: 													arg4 = str(myzodiac.chloricpct)
			arg5 = str(self.myzodiac.saltlevel)
			arg6 = self.myzodiac.errorstr
			arg7 = str(self.myzodiac.addsalt)
			arg8 = "Connected"
		else:
			arg2 = ""
			arg3 = 0
			arg4 = "-"
			arg5 = "-"
			arg6 = "-"
			arg7 = "-"
			arg8 = "No response from Zodiac!!!"
		self.sendHeader200WithMimetype()
		f = open("index.html" )	
		self.wfile.write(f.read()  % ( arg1, arg9,  arg2, arg3, arg4, arg5, arg6, arg7, arg8) )
		f.close()

	def sendDynamicWebFileRequest(self):
		if re.match('/index.html',self.path):
			self.SendIndex()
		else:
			return False
		return True
				
	def FindCommand(self):
		if re.match('/toggleConnection', self.path): 
			self.myzodiac.active = False if (self.myzodiac.active)  else True
			return True
		match = re.match('/setChlorine\?pct=([0-9]+)', self.path)
		if match:
			pct = (int(match.group(1),10))
			if not (pct<0 or pct>101): 
				self.myzodiac.chloricpct = (int(match.group(1),10))
		elif re.match('/rebootpi', self.path):
			os.system("reboot")	
		elif re.match('/gettime', self.path):
			os.system("/usr/sbin/ntpd -s")	
		else:
			return False
		return True

	


myzodiac 	= myZodiacTriClass( RS485Device , True )
myWebServer	= myWebServerClass(8081, myRequestHandler)
stopFlag 	= Event()
thread 		= MyThread(stopFlag, myzodiac)

try:
	thread.start()
	myWebServer.theRequestHandler.myzodiac = myzodiac
	myWebServer.run()
		
except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	stopFlag.set()
	exit()


