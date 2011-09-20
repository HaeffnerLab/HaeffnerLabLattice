from PyQt4 import QtGui, QtCore
from qtui.QCustomLevelTilt import QCustomLevelTilt
from twisted.internet.defer import inlineCallbacks

UpdateTime = 100 #in ms, how often data is checked for communication with the server

class COMPENSATION_CONTROL(QCustomLevelTilt):
    def __init__(self, reactor, parent=None):
        self.reactor = reactor
        QCustomLevelTilt.__init__(self,'Compensation',['c1','c2'],(-100,100), parent)
        self.connect()
    
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.server = yield self.cxn.compensation_box
        range1 = yield self.server.getrange(1)
        range2 = yield self.server.getrange(2)
        MinLevel = max(range1[0],range2[0])
        MaxLevel = min(range1[1],range2[1])
        self.setRange((MinLevel,MaxLevel))
        self.setStepSize(.1)
        #set initial values
        one = yield self.server.getcomp(1)
        two = yield self.server.getcomp(2)
        self.setValues(one,two)
        #connect functions
        self.onNewValues.connect(self.inputHasUpdated)
        ##start timer
        self.inputUpdated = False;
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
        
    def inputHasUpdated(self):
        self.inputUpdated = True
	
    @inlineCallbacks
    def sendToServer(self):
        if(self.inputUpdated):
            one = self.valueLeft.value()
            two =  self.valueRight.value()
            yield self.server.setcomp(1,one)
            yield self.server.setcomp(2,two)
            self.inputUpdated = False;
            
    def closeEvent(self, x):
        self.reactor.stop()
    	      
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    COMPENSATION_CONTROL = COMPENSATION_CONTROL(reactor)
    COMPENSATION_CONTROL.show()
    reactor.run()

 
