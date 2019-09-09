#!/usr/bin/env python
# coding=utf-8

from myZodiacTriClass import *
from time import sleep

RS485Device 	= "/dev/ttyUSB0"
myzodiac	= myZodiacTriClass( RS485Device, True )

myzodiac.sendCmdProbe()
myzodiac.readMsg()
myzodiac.sendCmdProbe()
myzodiac.readMsg()
myzodiac.sendCmdProbe()
myzodiac.readMsg()
myzodiac.sendCmdProbe()
myzodiac.readMsg()
myzodiac.chloricpct	= 100
myzodiac.sendCmdSetPercentage()
myzodiac.readMsg()
print (myzodiac.connected)


