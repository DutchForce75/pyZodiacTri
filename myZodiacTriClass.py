#!/usr/bin/env python
# coding=utf-8

"""
Zodiac TRI Serial AquaPure Rev L/M Protocol (9600baud 8N1):
Packets from master to ZodiacTri Slave:
	Header(self.DLE+self.STX): 		10 02
	Destination ID:				50
	Command:				00 | 11 | 14
	Args:					1 or 2 bytes
	Checksum:				1 byte
	Footer(self.DLE+self.ETX):		10 03

Example packets from master to ZodiacTri Slave:
	sendCmdProbe 				1002  50 00     62 1003
	sendCmdSetPercentage 34%		1002  50 11 22  95 1003
	sendCmdBoost 101%			1002  50 11 65  d8 1003 
	sendCmdGetID				1002  50 14 01  77 1003


Packets from ZodiacTri Slave to master:
	Header(self.DLE+self.STX): 		10 02
	Destination ID:				00
	Command:				01 | 03 | 12
	Args:					n bytes
	Checksum:				1 byte
	Footer(self.DLE+self.ETX):		10 03
	
Example packets from ZodiacTri Slave to master:
	response to sendCmdProbe		1002 00 01 0000 13 1003 
	response to sendCmdGetID		1002 00 03 015a4f444941432044554f000000000000 d8 1003
	response to sendCmdSetPercentage 34%	1002 00 16 1d020000 47 1003 
	response to sendCmdBoost 101%		1002 00 16 1d020000 47 1003  
	
The response of sendCmdSetPercentage and sendCmdBoost returns: Slave:<00><version><salt><error><add salt:LowByte><add salt:HighByte>
	where:
	<version>=0x16="salt/100+add salt"
	<error>= bit0=no flow, b1=low salt, b2=high salt, b3=general fault  (No flow : 00:16:28:01:00:00, Low Salt: 00:16:28:02:00:00, High Salt: 00:16:28:04:00:00, Gen Fault: 00:16:28:08:00:00)
	<salt>=ppm salt level/100
	<add salt>=<16bit signed word>=lb salt to be added
		
Zodiac needs signal every 20 seconds, otherwise it shuts off
"""


import serial
import serial.rs485
import struct
import threading
import sys
from time import sleep
import re

def log(*args):
	message = "%-16s: "%args[0]
	for arg in args[1:]:
			message += arg.__str__()+" "
	print message
		
class AqualinkInterface(object):
	def __init__(self, theName, theRS485Device, debugData=False):
		self.active			= True
		self.NUL = '\x00'
		self.DLE = '\x10'
		self.STX = '\x02'
		self.ETX = '\x03'
		self.STARTPACKET = self.DLE + self.STX		# 1002
		self.ENDPACKET 	= self.DLE	+ self.ETX		# 1003
		self.RS485Device = theRS485Device
		self.name = theName
		self.debugData = debugData
		if self.debugData: log(self.name, "opening RS485 port", self.RS485Device)
		self.port = serial.rs485.RS485(self.RS485Device, baudrate=9600, 
				bytesize=serial.EIGHTBITS, 
				parity=serial.PARITY_NONE, 
				stopbits=serial.STOPBITS_ONE,
				timeout=0)
		self.port.rs485_mode = serial.rs485.RS485Settings(False,True,None,None)
		self.msg = "\x00\x00"
		self.connected = False
		self.port.flushInput()
		self.port.flushOutput()
	
	def sync(self):
		self.msg = "\x00\x00"
		""" skip bytes until synchronized with the start of a message"""
		while (self.msg[-1] != self.STX) or (self.msg[-2] != self.DLE):
				if self.port.inWaiting()==0: 
					return
				self.msg += self.port.read(1)					
		self.msg = self.msg[-2:]
		if self.debugData: log(self.name, "synchronized")
		""" start up the read thread"""
		log(self.name, "ready")					
		
	def readRaw(self):
		while self.port.inWaiting()>0: 
			b = self.port.read(1)
			log(self.name, str(b).encode("hex"))

	def readMsg(self): 
		sleep(0.05)  		
		startFound = False
		endFound   = False
		self.msg = "\x00\x00"
		while self.port.inWaiting()>0 and startFound==False:                                                   
			self.msg += self.port.read(1)  																				#		 read 1 byte                     
			if self.msg[-2:] == self.STARTPACKET:
				startFound=True
			self.msg = self.msg[-2:]
		while self.port.inWaiting()>0 and endFound==False:                                                   
			self.msg += self.port.read(1)  																				#		 read 1 byte  
			if self.msg[-2:] == self.ENDPACKET:
				endFound=True
		""" parse the elements of the message"""              
		self.DLESTX = self.msg[0:2]
		dest = self.msg[2:3]
		cmd = self.msg[3:4]
		args = self.msg[4:-3]
		checksum = self.msg[-3:-2]
		self.DLEETX = self.msg[-2:]				
		if self.debugData: debugMsg = self.DLESTX.encode("hex")+" "+dest.encode("hex")+" "+\
			 cmd.encode("hex")+" "+args.encode("hex")+" "+\
			 checksum.encode("hex")+" "+self.DLEETX.encode("hex")

		""" stop reading if a message with a valid checksum is read"""
		if self.checksum(self.DLESTX+dest+cmd+args) == checksum:
				self.connected = True
				if self.debugData: log(self.name, "-->", debugMsg)
				return (dest, cmd, args)
		else:
				self.connected = False		
				if self.debugData: log(self.name, "-->", "")
				return []
														 

	def sendMsg(self, (dest, cmd, args)):
		msg = self.DLE+self.STX+dest+cmd+args
		msg = msg+self.checksum(msg)+self.DLE+self.ETX
		for i in range(2,len(msg)-2):												
			# if a byte in the message has the value \x10 insert a self.NUL after it
			if msg[i] == self.DLE:
				msg = msg[0:i+1]+self.NUL+msg[i+1:]
		if self.debugData: log(self.name, "<--", msg[0:2].encode("hex"), 
			msg[2:3].encode("hex"), msg[3:4].encode("hex"), 
			msg[4:-3].encode("hex"), msg[-3:-2].encode("hex"), 
			msg[-2:].encode("hex"))
		n = self.port.write(msg)	 

	def checksum(self, msg):
		""" Compute the checksum of a string of bytes."""								 
		return struct.pack("!B", reduce(lambda x,y:x+y, map(ord, msg)) % 256)

				
				
				
class myZodiacTriClass(AqualinkInterface):
	def __init__(self, theRS485device, debugData=False):	
		AqualinkInterface.__init__(self, "RS485", theRS485device, debugData)		
		self.ID 	= '\x50'
		self.ID_CHEMLINK = '\x82'
		self.CMD_PROBE 	= '\x00'
		self.CMD_GETPH 	= '\x01'
		self.CMD_SETPCT = '\x11'
		self.CMD_GETID 	= '\x14'
		self.chloricpct	= 100
		self.saltlevel 	= 0
		self.error	= 0 
		self.addsalt	= 0
		self.errorstr 	= ""
		self.connected  = False
			
	def readMsg(self):
		msg  = AqualinkInterface.readMsg(self)
		if msg:
			cmd  = msg[1]
			args = msg[2]
			if cmd:
				version = ord(cmd)				
				if version == 0x16:
					self.errorstr = ""
					errorslist = ("No flow", "Low salt", "High Salt", "Clean cell", "High current", "Low voltage", "Low watertemp", "Check PCB")
					self.saltlevel 		= ord(args[0])	#ord(statusstr[0])
					self.error 		= ord(args[1])	#ord(statusstr[1])
					self.addsalt		= ord(args[2]) + (ord(args[3])<<8)
					if self.error:
						for i in range(0, len(errorslist)-1):
							mask = 1<<(i)
							if self.error & mask:
								self.errorstr =self.errorstr + "-" + errorslist[i] + " "
		else:
			self.saltlevel 		= "-"
			self.error 		= "-"
			self.addsalt		= "-"
			

				
	

	def sendCmdProbe(self):
		""" sends 50:00 returns 00:01:00:00"""	
		self.sendMsg((self.ID, self.CMD_PROBE ,""))

	def sendCmdSetPercentage(self):
		""" sends 50:11:XX returns 00:version:salt:error:addsaltoLowByte:addsaltHighByte"""
		self.sendMsg((self.ID, self.CMD_SETPCT , chr(self.chloricpct)))
	
	def sendCmdBoost(self):
		""" sends 50:11:65 returns 00:version:salt:error:addsaltoLowByte:addsaltHighByte"""
		self.sendMsg((self.ID, self.CMD_SETPCT , chr(101))) 

	def sendCmdSwitchOff(self):
		""" sends 50:11:00 returns 00:version:salt:error:addsaltoLowByte:addsaltHighByte"""
		self.sendMsg((self.ID, self.CMD_SETPCT , chr(0)))		

	def sendCmdGetID(self):
		""" sends 50:14:01 returns 00:03:01:string"""
		self.sendMsg((self.ID, self.CMD_GETID , '\x01'))
	
	def sendCmdProbeChemlink(self):
		self.sendMsg((self.ID, self.CMD_PROBE ,""))
		self.sendMsg((self.ID_CHEMLINK, self.CMD_GETPH ,""))
