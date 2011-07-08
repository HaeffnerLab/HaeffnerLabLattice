import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
from decimal import Decimal

class QCustomLevelTilt(QtGui.QWidget):
    def __init__(self, title,channelNames, levelRange,tiltRange, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/leveltiltslidernew.ui')
        uic.loadUi(path,self)
        self.title.setText(title)
        self.labelLeft.setText(channelNames[0])
        self.labelRight.setText(channelNames[1])
        self.levelRange = levelRange
        #connect functions
    	self.sliderLevel.valueChanged.connect(self.sliderChanged)
    	self.sliderTilt.valueChanged.connect(self.sliderChanged)
    	self.spinLevel.valueChanged.connect(self.spinChanged)
    	self.spinTilt.valueChanged.connect(self.spinChanged)
        self.valueLeft.valueChanged.connect(self.lcdChanged)
        self.valueRight.valueChanged.connect(self.lcdChanged)
	#set widget properties
    	self.spinLevel.setRange(*levelRange)
    	self.sliderLevel.setRange(100*levelRange[0],100*levelRange[1])
    	self.spinTilt.setRange(*tiltRange)
    	self.sliderTilt.setRange(100.*tiltRange[0],100.*tiltRange[1])
    	self.valueLeft.setRange(*levelRange)
    	self.valueRight.setRange(*levelRange)
	#set LCDs initially
        self.spinChanged() 
        
        
    def spinChanged(self):
    	tilt = int(round(self.spinTilt.value()*100))
    	level = int(round(self.spinLevel.value()*100))
    	self.sliderLevel.setValue(level)
    	self.sliderTilt.setValue(tilt)
    	self.setLCD(level/100.,tilt/100.)

		
    def sliderChanged(self):
    	tilt = self.sliderTilt.value()
    	level = self.sliderLevel.value()
    	self.spinTilt.setValue(tilt/100.)
    	self.spinLevel.setValue(level/100.)
        
    def lcdChanged(self):
        c1 = self.valueLeft.value()*100.0
        c2 = self.valueRight.value()*100.0
        level = round( ( c1 + c2 ) / 2 )
        tilt = round( c2 - c1 )
        self.sliderLevel.setValue(level)
        self.sliderTilt.setValue(tilt)
        self.spinTilt.setValue(tilt/100.)
        self.spinLevel.setValue(level/100.)
        
    def setLCD(self,level,tilt):
    	one = level - tilt/2
    	two = level + tilt/2
    	one = self.checkBounds(one)
    	two = self.checkBounds(two)
    	self.valueRight.setValue(two)
    	self.valueLeft.setValue(one)

    def checkBounds(self, val):
    	if val < self.levelRange[0]:
    	      output = self.levelRange[0]
    	elif val > self.levelRange[1]:
    	      output = self.levelRange[1]
    	else:
    	      output = val
    	return output
	                
if __name__=='__main__':
	app = QtGui.QApplication(sys.argv)
	icon = QCustomLevelTilt('DC Voltages',['chA','chB'],(0.01,101),(-20,20))
	icon.show()
	app.exec_()

 
