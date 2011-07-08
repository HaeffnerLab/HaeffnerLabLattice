import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
import labrad
from qtui.QCustomLevelTilt import QCustomLevelTilt
import time

UpdateTime = 100 #in ms, how often data is checked for communication with the server

class COMPENSATION_CONTROL(QCustomLevelTilt):
    def __init__(self, server, parent=None):
        range1 = server.getrange(1)
        range2 = server.getrange(2)
        MinLevel = max(range1[0],range2[0])
        MaxLevel = min(range1[1],range2[1])
        QCustomLevelTilt.__init__(self,'Compensation',['c1','c2'],(MinLevel,MaxLevel), parent)
        self.setStepSize(.1)
        self.server = server
        #connect functions
        self.onNewValues.connect(self.inputHasUpdated)
        #set initial values
        [one, two] = [server.getcomp(1), server.getcomp(2)]
        self.setValues(one,two)
        ##start timer
        self.inputUpdated = False;
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
        
    def inputHasUpdated(self):
        self.inputUpdated = True
		
    def sendToServer(self):
        if self.server.updateddifferentcontext():
            print time.ctime(), 'COMPENSATION_CONTROL receiving data and updating itself'
            [one, two] = [self.server.getcomp(1), self.server.getcomp(2)]
            print 'new parameters', one, two
            self.setValues(one,two)
            self.inputUpdated = False
        if(self.inputUpdated):
            print time.ctime(), 'COMPENSATION_CONTROL sending data'
            one = self.valueLeft.value()
            two =  self.valueRight.value()
            self.server.setcomp(1,one)
            self.server.setcomp(2,two)
            print 'new data', one,two
            self.inputUpdated = False;
    	      
if __name__=='__main__':
    cxn = labrad.connect()
    server = cxn.compensation_box
    app = QtGui.QApplication(sys.argv)
    icon = COMPENSATION_CONTROL(server)
    icon.show()
    app.exec_()

 
