from PyQt4 import QtGui, uic
import os
from common.clients.connection import connection
from twisted.internet.defer import inlineCallbacks

basepath =  os.path.dirname(__file__)
path = os.path.join(basepath, "electrode.ui")
base, form = uic.loadUiType(path)

SIGNALID = 234534

class widget_ui(base, form):
    def __init__(self, parent = None):
        super(widget_ui, self).__init__(parent)
        self.setupUi(self)

class electrode_widget(QtGui.QFrame, widget_ui):
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
            yield self.initializeGUI()
            self.connect_layout()
            yield self.setupListeners()
        except Exception, e:
            print e
#             print 'Electrode client: Electrode Diagonalization not available'
            self.setDisabled(True)
        self.cxn.on_connect['Electrode Diagonalization'].append( self.reinitialize)
        self.cxn.on_disconnect['Electrode Diagonalization'].append( self.disable)
    
    @inlineCallbacks
    def initializeGUI(self):
        server = self.cxn.servers['Electrode Diagonalization']
        comp_angle = yield server.compensation_angle()
        endcap_angle = yield server.endcap_angle()
        voltage_priority = yield server.voltage_priority()
        self.set_widget_blocking(self.comp_angle, comp_angle['deg'])
        self.set_widget_blocking(self.endcap_angle, endcap_angle['deg'])
        self.do_set_voltage_priority(voltage_priority)
        yield self.get_all_voltages()
        yield self.get_all_fields()
    
    def set_widget_blocking(self, widget, value):
        widget.blockSignals(True)
        widget.setValue(value)
        widget.blockSignals(False)
    
    def do_set_voltage_priority(self, voltage_priority):
        self.endcap_angle.blockSignals(True)
        if voltage_priority:
            self.combo.setCurrentIndex(0)
        else:
            self.combo.setCurrentIndex(1)
        self.endcap_angle.blockSignals(False)
    
    @inlineCallbacks
    def get_all_voltages(self):
        server = self.cxn.servers['Electrode Diagonalization']
        for name,widget in [('C1', self.comp1), ('C2',self.comp2),('D1', self.endcap1),('D2', self.endcap2)]:
            voltage = yield server.voltage(name)
            self.set_widget_blocking(widget, voltage['V'])
    
    @inlineCallbacks
    def get_all_fields(self):
        server = self.cxn.servers['Electrode Diagonalization']
        for name,widget in [('Ex', self.Ex), ('Ey',self.Ey),('Ez', self.Ez),('w_z_sq', self.w_z_sq)]:
            value = yield server.field(name)
            self.set_widget_blocking(widget, value)
    
    def connect_layout(self):
        for name, widget in [('C1', self.comp1), ('C2',self.comp2),('D1', self.endcap1),('D2', self.endcap2)]:
            widget.valueChanged.connect(self.voltage_setter(name))
        for name,widget in [('Ex', self.Ex), ('Ey',self.Ey),('Ez', self.Ez),('w_z_sq', self.w_z_sq)]:
            widget.valueChanged.connect(self.field_setter(name))
        self.combo.currentIndexChanged.connect(self.on_new_priority)
        self.endcap_angle.valueChanged.connect(self.on_new_endcap_angle)
        self.comp_angle.valueChanged.connect(self.on_new_comp_angle)
    
    @inlineCallbacks
    def on_new_endcap_angle(self, value):
        server = self.cxn.servers['Electrode Diagonalization']
        yield server.endcap_angle(self.WithUnit(value,'deg'))
    
    @inlineCallbacks
    def on_new_comp_angle(self, value):
        server = self.cxn.servers['Electrode Diagonalization']
        yield server.compensation_angle(self.WithUnit(value,'deg'))
    
    @inlineCallbacks
    def on_new_priority(self, index):
        server = self.cxn.servers['Electrode Diagonalization']
        if index == 0:
            yield server.voltage_priority(True)
        elif index == 1:
            yield server.voltage_priority(False)
        
    
    def voltage_setter(self, name):
        @inlineCallbacks
        def set_voltage(value):
            server = self.cxn.servers['Electrode Diagonalization']
            yield server.voltage(name, self.WithUnit(value, 'V'))
        return set_voltage
    
    def field_setter(self, name):
        @inlineCallbacks
        def set_voltage(value):
            server = self.cxn.servers['Electrode Diagonalization']
            yield server.field(name, value)
        return set_voltage
    
    @inlineCallbacks
    def setupListeners(self):
        server = self.cxn.servers['Electrode Diagonalization']
        yield server.signal__new_value(SIGNALID, context = self.context)
        yield server.addListener(listener = self.followSignal, source = None, ID = SIGNALID, context = self.context)

    def followSignal(self, context, (name,value)):
        if name == 'C1':
            self.set_widget_blocking(self.comp1, value)
        elif name == 'C2':
            self.set_widget_blocking(self.comp2, value)
        elif name == 'D1':
            self.set_widget_blocking(self.endcap1, value)
        elif name == 'D2':
            self.set_widget_blocking(self.endcap2, value)
        if name == 'Ex':
            self.set_widget_blocking(self.Ex, value)
        elif name == 'Ey':
            self.set_widget_blocking(self.Ey, value)
        elif name == 'Ez':
            self.set_widget_blocking(self.Ez, value)
        elif name == 'w_z_sq':
            self.set_widget_blocking(self.w_z_sq, value)
        elif name == 'comp_angle':
            self.set_widget_blocking(self.comp_angle, value)
        elif name == 'endcap_angle':
            self.set_widget_blocking(self.endcap_angle, value)
        elif name == 'priority':
            self.do_set_voltage_priority(value)
        
    @inlineCallbacks
    def reinitialize(self):
        self.setDisabled(False)
        if self.initialized:
            yield self.initializeGUI()
            server = self.cxn.servers['Electrode Diagonalization']
            yield server.signal__new_value(SIGNALID, context = self.context)
        else:
            yield self.initializeGUI()
            yield self.setupListeners()
    
    @inlineCallbacks
    def disable(self):
        self.setDisabled(True)
        yield None
    
    def closeEvent(self, x):
        self.reactor.stop()  
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    electrodes = electrode_widget(reactor)
    electrodes.show()
    reactor.run()