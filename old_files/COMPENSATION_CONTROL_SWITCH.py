import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
import labrad
from qtui.QCustomLevelTiltSwitch import QCustomLevelTilt

MinLevel = -500
MaxLevel = 0
MaxTilt = 500 #maximum allowed tilt
UpdateTime = 100 #in ms, how often data is checked for communication with the server

class COMPENSATION_CONTROL(QCustomLevelTilt):
    def __init__(self, server, parent=None):
        QCustomLevelTilt.__init__(self,'Compensation',['c1','c2'],(MinLevel,MaxLevel),(-MaxTilt,MaxTilt), parent)
        self.server = server
        #connect functions
    	self.spinLevel.valueChanged.connect(self.inputHasUpdated)
    	self.spinTilt.valueChanged.connect(self.inputHasUpdated)
        #set initial values
        one = server.getcomp(1)
        two = server.getcomp(2)
        level = float(one + two)/2
        tilt = float(two - one)
        self.spinLevel.setValue(level)
        self.spinTilt.setValue(tilt)
        ##start timer
        self.inputUpdated = False;
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
        

        
    def inputHasUpdated(self):
	   self.inputUpdated = True
		
    #if inputs are updated by user, send the LCD values to server
    def sendToServer(self):
    	if(self.inputUpdated):
    	      print 'COMPENSATION_CONTROL sending data'
    	      one = self.valueLeft.value()
    	      two =  self.valueRight.value()
    	      self.server.setcomp(1,one)
              self.server.setcomp(2,two)
    	      self.inputUpdated = False;
    	      
if __name__=='__main__':
    cxn = labrad.connect()
    server = cxn.compensation_box
    app = QtGui.QApplication(sys.argv)
    icon = COMPENSATION_CONTROL(server)
    icon.show()
    app.exec_()

 
