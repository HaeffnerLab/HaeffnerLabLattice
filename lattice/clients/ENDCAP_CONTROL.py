from PyQt4 import QtGui, QtCore
from qtui.QCustomLevelTilt import QCustomLevelTilt
from twisted.internet.defer import inlineCallbacks

MinLevel = -9.0
MaxLevel = 9.0
UpdateTime = 100 #in ms, how often data is checked for communication with the server

class ENDCAP_CONTROL(QCustomLevelTilt):
    def __init__(self, reactor, parent=None):
        self.reactor = reactor
        super(ENDCAP_CONTROL, self).__init__('DC Endcaps',['d1','d2'],(MinLevel,MaxLevel), parent)
        self.connect()
    
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.units import WithUnit
        self.WithUnit = WithUnit
        self.cxn = yield connectAsync()
        self.server = yield self.cxn.dac
        #set initial values
        one = yield self.server.get_voltage("endcap1")
        two = yield self.server.get_voltage("endcap2")
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
            yield self.server.set_voltage("endcap1",self.WithUnit(one, "V"))
            yield self.server.set_voltage("endcap2",self.WithUnit(two, "V"))
            self.inputUpdated = False;
    
    def closeEvent(self, x):
        self.reactor.stop()
    
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    ENDCAP_CONTROL = ENDCAP_CONTROL(reactor)
    ENDCAP_CONTROL.show()
    reactor.run()