#!/usr/bin/python
# -*- coding: utf-8 -*-

# slider.py

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

MinLevel = 50
MaxLevel = 300
MinTilt = -200
MaxTilt = 200
UpdateTime = 100 #in ms, how often data is checked for communication with the server
ServerName = ''

#TODO1 implement with actual server
#SETUP QtDesigner import

class Slider(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setGeometry(300, 300, 500, 150)
        self.setWindowTitle('DCcontrol')
        #set up slider for level
        self.sliderLevel = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sliderLevel.setGeometry(130, 40, 100, 30)
        self.sliderLevel.setRange(MinLevel, MaxLevel)
        self.connect(self.sliderLevel, QtCore.SIGNAL('valueChanged(int)'), self.sliderChanged)
        self.sliderTilt = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sliderTilt.setGeometry(130, 80, 100, 30)
        self.sliderTilt.setRange(MinTilt,MaxTilt)
        self.connect(self.sliderTilt, QtCore.SIGNAL('valueChanged(int)'), self.sliderChanged)
        
        self.spinLevel = QtGui.QSpinBox(self)
        self.spinLevel.setGeometry(300,40,80,30)
        self.spinLevel.setRange(MinLevel,MaxLevel)
        self.connect(self.spinLevel, QtCore.SIGNAL('valueChanged(int)'), self.spinChanged)
        self.spinLevel.setKeyboardTracking(False)

        self.spinTilt = QtGui.QSpinBox(self)
        self.spinTilt.setGeometry(300,80,80,30)
        self.spinTilt.setRange(MinTilt,MaxTilt)
        self.connect(self.spinTilt, QtCore.SIGNAL('valueChanged(int)'), self.spinChanged)
        self.spinTilt.setKeyboardTracking(False)
	

        self.label = QtGui.QLabel(self)
        self.label.setText('Level')
        self.label.setGeometry(260, 40, 80, 30)
        
        self.label = QtGui.QLabel(self)
        self.label.setText('Tilt')
        self.label.setGeometry(260, 80, 80, 30)
        
        self.inputUpdated = False;
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer,QtCore.SIGNAL("timeout()"),self.sendToServer)
        self.timer.start(UpdateTime)
        


        
    def spinChanged(self):
        tilt = self.spinTilt.value()
        level = self.spinLevel.value()
        self.sliderLevel.setSliderPosition(level)
        self.sliderTilt.setSliderPosition(tilt)
        self.inputUpdated = True;
		
    def sliderChanged(self):
        tilt = self.sliderTilt.value()
        level = self.sliderLevel.value()
        self.spinTilt.setValue(tilt)
        self.spinLevel.setValue(level)
        self.inputUpdated = True;
      
    def sendToServer(self):
        if(self.inputUpdated):
            print 'should send'
            print self.sliderTilt.value()
            print self.sliderLevel.value()
            self.inputUpdated = False;
    


app = QtGui.QApplication(sys.argv)
icon = Slider()
icon.show()
app.exec_()

 
