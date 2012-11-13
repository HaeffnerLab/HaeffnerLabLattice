#!/usr/bin/python
# -*- coding: utf-8 -*-
portA = 'COM6'
portB = 'COM5'

import serial 
serA = serial.Serial(portA)
serB = serial.Serial(portB)

#function converts input voltage to microcontroller scale
#1023 is 4000 volts, scale is linear
def VoltagetoFormat(volt):
  	if (volt < 0 or volt > 4000):
	      volt = 0
	      print 'wrong voltage entered'
	num = round((volt/4000.0)*1023)
	return int(num)

#takes a a number of converts it to a string understood by microcontroller, i.e 23 -> C0023!
def MakeComString(num):
	comstring = 'C' + str(num).zfill(4) + '!'
	return comstring

while(True):
	bd = raw_input("enter voltages in format A/B: ")
	a,b = bd.split('/')
	print a
	print b
	strA = MakeComString(VoltagetoFormat(float(a)))
	strB = MakeComString(VoltagetoFormat(float(b)))
	serA.write(strA)
	serB.write(strB)
