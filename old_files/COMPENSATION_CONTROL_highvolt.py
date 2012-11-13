import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
import labrad
from qtui.QCustomLevelTilt import QCustomLevelTilt

MinLevel = 100
MaxLevel = 1000
MaxTilt = 100 #maximum allowed tilt
UpdateTime = 100 #in ms, how often data is checked for communication with the server

class COMPENSATION_CONTROL(QCustomLevelTilt):
    def __init__(self, serverA, serverB, parent=None):
        QCustomLevelTilt.__init__(self,'Compensation',['HighVolt A','HighVolt B'],(MinLevel,MaxLevel),(-MaxTilt,MaxTilt), parent)
        self.serverA = serverA
        self.serverB = serverB
        #connect functions
    	self.spinLevel.valueChanged.connect(self.inputHasUpdated)
    	self.spinTilt.valueChanged.connect(self.inputHasUpdated)
        #set initial values
        one = serverA.getvoltage()
        two = serverB.getvoltage()
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
    	      print 'ENDCAP_CONTROL sending data'
    	      one = self.valueLeft.value()
    	      two =  self.valueRight.value()
    	      self.serverA.setvoltage(one)
              self.serverB.setvoltage(two)
    	      self.inputUpdated = False;
    	      
if __name__=='__main__':
    cxn = labrad.connect()
    serverA = cxn.highvolta
    serverB = cxn.highvoltb
    app = QtGui.QApplication(sys.argv)
    icon = COMPENSATION_CONTROL(serverA,serverB)
    icon.show()
    app.exec_()

 
