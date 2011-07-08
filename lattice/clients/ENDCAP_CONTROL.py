import sys
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad
from qtui.QCustomLevelTilt import QCustomLevelTilt

MinLevel = 0
MaxLevel = 40
UpdateTime = 100 #in ms, how often data is checked for communication with the server

class ENDCAP_CONTROL(QCustomLevelTilt):
    def __init__(self, server, parent=None):
        QCustomLevelTilt.__init__(self,'DC Endcaps',['d1','d2'],(MinLevel,MaxLevel), parent)
        self.server = server
    	#connect functions
        self.onNewValues.connect(self.inputHasUpdated)
        #set initial values
        one = server.getEndCap(1)
        two = server.getEndCap(2)
        self.valueLeft.setValue(one)
        self.valueRight.setValue(two)
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

 
