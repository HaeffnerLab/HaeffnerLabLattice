#!/usr/bin/python
# -*- coding: utf-8 -*-

# slider.py

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad

MinLevel = 50
MaxLevel = 999
MaxTilt = 200 #maximum allowed tilt
UpdateTime = 100 #in ms, how often data is checked for communication with the server

#cxn = labrad.connect('localhost')
#server = cxn.lattice_pc_dc_server

#TODO1 implement with actual server

class DC_CONTROL(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        uic.loadUi('QtDesignerUI/dcfrontend.ui',self)
	#connect functions
        self.connect(self.sliderLevel, QtCore.SIGNAL('valueChanged(int)'), self.sliderChanged)
        self.connect(self.sliderTilt, QtCore.SIGNAL('valueChanged(int)'), self.sliderChanged)
	self.connect(self.spinLevel, QtCore.SIGNAL('valueChanged(int)'), self.spinChanged)
	self.connect(self.spinTilt, QtCore.SIGNAL('valueChanged(int)'), self.spinChanged)
	#set widget properties
	self.spinLevel.setKeyboardTracking(False)
	self.spinTilt.setKeyboardTracking(False)
	self.spinLevel.setRange(MinLevel,MaxLevel)
	self.sliderLevel.setRange(MinLevel,MaxLevel)
	self.spinTilt.setRange(-MaxTilt,MaxTilt)
	self.sliderTilt.setRange(-MaxTilt,MaxTilt)
	#set LCDs initially
	self.spinChanged() 
        self.inputUpdated = False;
        #start timer
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer,QtCore.SIGNAL("timeout()"),self.sendToServer)
        self.timer.start(UpdateTime)
        
        
    def spinChanged(self):
	tilt = self.spinTilt.value()
	level = self.spinLevel.value()
	self.sliderLevel.setSliderPosition(level)
	self.sliderTilt.setSliderPosition(tilt)
	self.setLCD(level,tilt)
	self.inputUpdated = True;
		
    def sliderChanged(self):
	tilt = self.sliderTilt.value()
	level = self.sliderLevel.value()
	self.spinTilt.setValue(tilt)
	self.spinLevel.setValue(level)
	self.setLCD(level,tilt)
	self.inputUpdated = True;
 
    def setLCD(self,level,tilt):
	red = (level - tilt)
	blue =(level + tilt)
	red = self.checkBounds(red)
	blue = self.checkBounds(blue)
	self.lcdRed.display(red)
	self.lcdBlue.display(blue)

    def checkBounds(self, val):
	if val < MinLevel:
	      output = MinLevel
	elif val > MaxLevel:
	      output = MaxLevel
	else:
	      output = val
	return output
	            
    #if inputs are updated by user, send the LCD values to server
    def sendToServer(self):
	if(self.inputUpdated):
	      print 'DC_CONTRL_GUI sending data'
	      red =  self.lcdRed.value()
	      blue = self.lcdBlue.value()
	      server.set(blue,red)
	      self.inputUpdated = False;
    


app = QtGui.QApplication(sys.argv)
icon = DC_CONTROL()
icon.show()
app.exec_()

 
