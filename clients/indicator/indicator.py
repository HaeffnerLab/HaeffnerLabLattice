from PyQt4 import QtGui, uic
import os
from common.clients.connection import connection
from twisted.internet.defer import inlineCallbacks

basepath =  os.path.dirname(__file__)
path = os.path.join(basepath, "indicator.ui")
base, form = uic.loadUiType(path)

SIGNALID = 345231

class widget_ui(base, form):
    def __init__(self, parent = None):
        super(widget_ui, self).__init__(parent)
        self.setupUi(self)

class indicator_widget(QtGui.QFrame, widget_ui):
    def __init__(self,reactor,cxn = None, parent=None):
        self.reactor = reactor
        self.cxn = cxn
        QtGui.QDialog.__init__(self)
        widget_ui.__init__(self)
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
            yield self.initialize_gui()
            yield self.setupListeners()
        except Exception, e:
            print e
            self.setDisabled(True)
        yield self.cxn.add_on_connect('ParameterVault', self.reinitialize)
        yield self.cxn.add_on_disconnect('ParameterVault', self.disable)
    
    @inlineCallbacks
    def initialize_gui(self):
        yield self.populate_gui()
    
    @inlineCallbacks
    def populate_gui(self):
        for cb in [self.sideband_cooling, self.optical_pumping, self.background_heating]:     
            cb.setDisabled(True)
        self.sideband_cooling.setDisabled(True)
        pv = yield self.cxn.get_server('ParameterVault')
        op = yield pv.get_parameter(('OpticalPumping','optical_pumping_enable'))
        sb = yield pv.get_parameter(('SidebandCooling','sideband_cooling_enable'))
        heating = yield pv.get_parameter(('Heating','background_heating_time'))
        self.optical_pumping.setChecked(op)
        self.sideband_cooling.setChecked(sb)
        self.background_heating.setChecked(heating['s'] > 0)
    
    @inlineCallbacks
    def setupListeners(self):
        server = yield self.cxn.get_server('ParameterVault')
        yield server.signal__parameter_change(SIGNALID, context = self.context)
        yield server.addListener(listener = self.followSignal, source = None, ID = SIGNALID, context = self.context)
        self.initialized = True

    @inlineCallbacks
    def followSignal(self, context, name):
        pv = yield self.cxn.get_server('ParameterVault')
        if name == ('OpticalPumping','optical_pumping_enable'):
            op = yield pv.get_parameter(name)
            self.optical_pumping.setChecked(op)
        elif name == ('SidebandCooling','sideband_cooling_enable'):
            sb = yield pv.get_parameter(name)
            self.sideband_cooling.setChecked(sb)
        elif name == ('Heating','background_heating_time'):
            heating = yield pv.get_parameter(name)
            self.background_heating.setChecked(heating['s'] > 0)
            
    @inlineCallbacks
    def reinitialize(self):
        self.setDisabled(False)
        yield self.populate_gui()
        if not self.initialized:
            yield self.setupListeners()
        else:
            server = yield self.cxn.get_server('ParameterVault')
            yield server.signal__parameter_change(SIGNALID, context = self.context)
            
    def disable(self):
        self.setDisabled(True)
    
    def closeEvent(self, x):
        self.reactor.stop()  
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    electrodes = indicator_widget(reactor)
    electrodes.show()
    reactor.run()