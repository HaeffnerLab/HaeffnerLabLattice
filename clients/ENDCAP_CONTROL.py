from PyQt4 import QtGui
from qtui.QCustomLevelTilt import QCustomLevelTilt
from twisted.internet.defer import inlineCallbacks
from common.clients.connection import connection

MinLevel = -9.0
MaxLevel = 9.0

SIGNALID = 139156

class ENDCAP_CONTROL(QCustomLevelTilt):
    def __init__(self, reactor, cxn = None, parent=None):
        self.reactor = reactor
        self.cxn = cxn
        super(ENDCAP_CONTROL, self).__init__('DC Endcaps',['d1','d2'],(MinLevel,MaxLevel), parent)
        self.connect()
        self.initialized = False
    
    @inlineCallbacks
    def connect(self):
        from labrad.units import WithUnit
        from labrad.types import Error
        self.WithUnit = WithUnit
        self.Error = Error
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            yield self.initializeGUI()
            yield self.setupListeners()
        except Exception, e:
            print 'ENDCAP_CONTROL: DAC not available'
            self.setDisabled(True)
        self.cxn.on_connect['DAC'].append( self.reinitialize)
        self.cxn.on_disconnect['DAC'].append( self.disable)
    
    @inlineCallbacks
    def initializeGUI(self):
        yield self.get_values_from_server()
        self.onNewValues.connect(self.on_new_values)        
        self.initialized = True
        
    @inlineCallbacks
    def get_values_from_server(self):
        server = self.cxn.servers['DAC']
        one = yield server.get_voltage("endcap1")
        two = yield server.get_voltage("endcap2")
        self.setValues(one['V'], two['V'])
        
    @inlineCallbacks
    def reinitialize(self):
        self.setDisabled(False)
        if self.initialized:
            server = self.cxn.servers['DAC']
            yield self.get_values_from_server()
            yield server.signal__new_voltage(SIGNALID, context = self.context)
        else:
            yield self.initializeGUI()
            yield self.setupListeners()
           
    @inlineCallbacks
    def setupListeners(self):
        server = self.cxn.servers['DAC']
        yield server.signal__new_voltage(SIGNALID, context = self.context)
        yield server.addListener(listener = self.followSignal, source = None, ID = SIGNALID, context = self.context)
    
    @inlineCallbacks
    def followSignal(self, x, (channel_name, voltage)):
        yield None
        pass
#        new new level-til that handles setting the voltage channels separately
#        yield self.get_values_from_server()
    
    @inlineCallbacks       
    def on_new_values(self):
        #        new new level-tilt that handles setting the voltage channels separately
        server = self.cxn.servers['DAC']
        one = self.valueLeft.value()
        two =  self.valueRight.value()
        for name, val in [('endcap1', one), ('endcap2',two)]:
            try:
                yield server.set_voltage(name,self.WithUnit(val))
            except self.Error as e:
                yield self.get_values_from_server()
                self.displayError(e.msg)
                break
            
    @inlineCallbacks
    def disable(self):
        self.setDisabled(True)
        yield None
        
    def displayError(self, text):
        message = QtGui.QMessageBox()
        message.setText(text)
        message.exec_()
    
    def closeEvent(self, x):
        self.reactor.stop()
    
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    ENDCAP_CONTROL = ENDCAP_CONTROL(reactor)
    ENDCAP_CONTROL.show()
    reactor.run()