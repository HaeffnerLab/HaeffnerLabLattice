from PyQt4 import QtGui, QtCore
from qtui.SliderSpin import SliderSpin
from twisted.internet.defer import inlineCallbacks, returnValue

UpdateTime = 100 #in ms, how often data is checked for communication with the server

class INTENSITY_CONTROL(SliderSpin):
    def __init__(self, reactor ,parent=None):
        super(INTENSITY_CONTROL, self).__init__('397 Intensity','mV',(0,2500),(0,2500),parent)
        self.reactor = reactor
        self.connect()
    
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.server = yield self.cxn.dc_box
        self.registry = yield self.cxn.registry
        [Min397Intensity,Max397Intensity] = yield self.getRangefromReg()
        self.minrange.setValue(Min397Intensity)
        self.maxrange.setValue(Max397Intensity)
        intensity = yield self.server.getintensity397()
        self.spin.setValue(intensity)
        #connect functions
        self.spin.valueChanged.connect(self.on397Update)
        self.minrange.valueChanged.connect(self.saveNewRange)
        self.maxrange.valueChanged.connect(self.saveNewRange)
        #start timer
        self.updated397 = False;
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
    
    @inlineCallbacks
    def saveNewRange(self, val):
        [min397,max397] = [self.minrange.value(), self.maxrange.value()]
        yield self.registry.cd(['','Clients','Intensity Control'],True)
        yield self.registry.set('range397', [min397,max397])
         
    def on397Update(self):
        self.updated397 = True
    
    @inlineCallbacks
    def getRangefromReg(self):
        yield self.registry.cd(['','Clients','Intensity Control'],True)
        try:
            [min397,max397] = yield self.registry.get('range397')
        except Error, e:
            if e.code is 21:
                [min397,max397] = [0,2500] #default min and max levels
        returnValue( [min397,max397] )
	
	#if inputs are updated by user, send the values to server
    @inlineCallbacks
    def sendToServer(self):
        if(self.updated397):
            yield self.server.setintensity397(self.spin.value())
            self.updated397 = False
        
    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    INTENSITY_CONTROL = INTENSITY_CONTROL(reactor)
    INTENSITY_CONTROL.show()
    reactor.run()