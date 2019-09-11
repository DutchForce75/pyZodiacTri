#!/usr/bin/env python
# coding=utf-8

from myZodiacTriClass import *
from time import sleep

RS485Device 	= "/dev/tty.lpss-serial2"
myzodiac	= myZodiacTriClass( RS485Device, True )


try:
	myzodiac.port.flushInput()
	myzodiac.port.flushOutput()

except KeyboardInterrupt:
	print '^C received, shutting down the script'
	exit()


ID_CHEMLINK 		= '\x80'
CMD_CHEMLINK_PROBE	= '\x00'
CMD_CHEMLINK_STATUS	= '\x02'

for i in range(0,255):
	for n in range(0,3):
		myzodiac.sendMsg((chr(i), '\x00' , ""))	
		myzodiac.readMsg()
		sleep(0.2)
	

	

