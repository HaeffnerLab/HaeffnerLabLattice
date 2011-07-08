import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad

MinLevel = 0
MaxLevel = 40
MaxTilt = 20 #maximum allowed tilt
UpdateTime = 100 #in ms, how often data is checked for communication with the server

class ENDCAP_CONTROL(QtGui.QWidget):
    def __init__(self, server, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/dcfrontend.ui')
        uic.loadUi(path,self)
        self.server = server
    	#connect functions
        self.connect(self.sliderLevel, QtCore.SIGNAL('valueChanged(int)'), self.sliderChanged)
        self.connect(self.sliderTilt, QtCore.SIGNAL('valueChanged(int)'), self.sliderChanged)
    	self.connect(self.spinLevel, QtCore.SIGNAL('valueChanged(double)'), self.spinChanged)
    	self.connect(self.spinTilt, QtCore.SIGNAL('valueChanged(double)'), self.spinChanged)
    	#set widget properties
    	self.spinLevel.setKeyboardTracking(False)
    	self.spinTilt.setKeyboardTracking(False)
    	self.spinLevel.setRange(MinLevel,MaxLevel)
    	self.sliderLevel.setRange(100*MinLevel,100*MaxLevel)
    	self.spinTilt.setRange(-MaxTilt,MaxTilt)
    	self.sliderTilt.setRange(-100*MaxTilt,100*MaxTilt)
        #set initial values
        one = server.getEndCap(1)
        two = server.getEndCap(2)
        level = float(one + two)/2
        tilt = float(one - two)/2
        self.sliderLevel.setValue(level)
        self.spinLevel.setValue(level)
        self.sliderTilt.setValue(tilt)
        self.spinTilt.setValue(tilt)
	    #set LCDs initially
        self.spinChanged() 
        self.inputUpdated = False;
        #start timer
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer,QtCore.SIGNAL("timeout()"),self.sendToServer)
        self.timer.start(UpdateTime)
        
        
    def spinChanged(self):
    	tilt = int(round(self.spinTilt.value()*100))
    	level = int(round(self.spinLevel.value()*100))
    	self.sliderLevel.setValue(level)
    	self.sliderTilt.setValue(tilt)
    	self.setLCD(level/100.,tilt/100.)
    	self.inputUpdated = True;
		
    def sliderChanged(self):
    	tilt = self.sliderTilt.value()
    	level = self.sliderLevel.value()
    	self.spinTilt.setValue(tilt/100.)
    	self.spinLevel.setValue(level/100.)
    	self.setLCD(level/100.,tilt/100.)
    	self.inputUpdated = True;
 
    def setLCD(self,level,tilt):
    	two = (level - tilt)
    	one =(level + tilt)
    	one = self.checkBounds(one)
    	two = self.checkBounds(two)
    	self.lcdTwo.display( '%.2f' %two)
    	self.lcdOne.display(' %.2f' %one)

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
    	      print 'ENDCAP_CONTROL sending data'
    	      two =  self.lcdTwo.value()
    	      one = self.lcdOne.value()
    	      self.server.setendcap(1,one)
              self.server.setendcap(2,two)
    	      self.inputUpdated = False;
    
if __name__=='__main__':
	cxn = labrad.connect()
	server = cxn.dc_box
	app = QtGui.QApplication(sys.argv)
	icon = ENDCAP_CONTROL(server)
	icon.show()
	app.exec_()

 
