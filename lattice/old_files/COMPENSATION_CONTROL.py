import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad

MinLevel = -18
MaxLevel = 18
MaxTilt = 18 #maximum allowed tilt
UpdateTime = 100 #in ms, how often data is checked for communication with the server

cxn = labrad.connect()
server = cxn.dc_box

class DC_CONTROL(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/compensationfrontend.ui')
        uic.loadUi(path,self)
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
    	      print 'DC_CONTRL_GUI sending data'
    	      two =  self.lcdTwo.value()
    	      one = self.lcdOne.value()
    	      print one,two
    	      server.setcomp(1,one)
              server.setcomp(2,two)
    	      self.inputUpdated = False;
    


app = QtGui.QApplication(sys.argv)
icon = DC_CONTROL()
icon.show()
app.exec_()

 
