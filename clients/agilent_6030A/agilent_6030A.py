from PyQt4 import QtGui, uic
import os
from common.clients.connection import connection
from twisted.internet.defer import inlineCallbacks

basepath =  os.path.dirname(__file__)
path = os.path.join(basepath, "agilent_6030A.ui")
base, form = uic.loadUiType(path)

class widget_ui(base, form):
    def __init__(self, parent = None):
        super(widget_ui, self).__init__(parent)
        self.setupUi(self)

class agilent_6030a(QtGui.QFrame, widget_ui):
    def __init__(self,reactor,cxn = None, parent=None):
        self.reactor = reactor
        self.cxn = cxn
        QtGui.QDialog.__init__(self)
        widget_ui.__init__(self)
        self.connect()
    
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
            yield self.initialize_gui()
        except Exception, e:
            print e
            self.setDisabled(True)
        self.cxn.on_connect['Agilent 6030A Server'].append( self.reinitialize)
        self.cxn.on_disconnect['Agilent 6030A Server'].append( self.disable)
    
    @inlineCallbacks
    def initialize_gui(self):
        yield self.populate_gui()
        self.connect_gui()
    
    @inlineCallbacks
    def populate_gui(self):
        server = self.cxn.servers['Agilent 6030A Server']
        voltage = yield server.voltage()
        current = yield server.current()
        self.set_widget_blocking(self.voltage, voltage['V'])
        self.set_widget_blocking(self.current, current['A'])
    
    def set_widget_blocking(self, widget, value):
        widget.blockSignals(True)
        widget.setValue(value)
        widget.blockSignals(False)
    
    def connect_gui(self):
        self.current.valueChanged.connect(self.on_new_current)
        self.voltage.valueChanged.connect(self.on_new_voltage)
    
    @inlineCallbacks
    def on_new_current(self, current):
        server = self.cxn.servers['Agilent 6030A Server']
        yield server.current(self.WithUnit(current, 'A'))
    
    @inlineCallbacks
    def on_new_voltage(self, voltage):
        server = self.cxn.servers['Agilent 6030A Server']
        yield server.voltage(self.WithUnit(voltage, 'V'))
            
    @inlineCallbacks
    def reinitialize(self):
        self.setDisabled(False)
        yield self.populate_gui()
            
    def disable(self):
        self.setDisabled(True)
    
    def closeEvent(self, x):
        self.reactor.stop()  
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = agilent_6030a(reactor)
    widget.show()
    reactor.run()