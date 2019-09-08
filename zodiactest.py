#!/usr/bin/env python
# coding=utf-8

from myZodiacTriClass import *
from time import sleep

RS485Device 	= "/dev/ttyUSB0"
myzodiac	= myZodiacTriClass( RS485Device, True )


try:
	myzodiac.port.flushInput()
	myzodiac.port.flushOutput()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	exit()

while(1):
	myzodiac.sendCmdProbe()
	myzodiac.readMsg()
	myzodiac.sendCmdGetID()
	myzodiac.readMsg()
	sleep(0.5)

