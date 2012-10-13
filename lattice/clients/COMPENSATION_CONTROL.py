from PyQt4 import QtGui, QtCore
from qtui.QCustomLevelTilt import QCustomLevelTilt
from twisted.internet.defer import inlineCallbacks

MinLevel = -40.0
MaxLevel = 40.0
UpdateTime = 100 #in ms, how often data is checked for communication with the server

class COMPENSATION_CONTROL(QCustomLevelTilt):
    def __init__(self, reactor, parent=None):
        self.reactor = reactor
        super(COMPENSATION_CONTROL, self).__init__('Compensation',['c1','c2'],(MinLevel,MaxLevel), parent)
        self.connect()
    
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad import types as T
        self.T = T
        self.cxn = yield connectAsync()
        self.server = yield self.cxn.dac
        #set initial values
        one = yield self.server.get_voltage("comp1")
        two = yield self.server.get_voltage("comp2")
        self.valueLeft.setValue(one)
        self.valueRight.setValue(two)
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
            yield self.server.set_voltage("comp1",self.T.Value(one, "V"))
            yield self.server.set_voltage("comp2",self.T.Value(two, "V"))
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