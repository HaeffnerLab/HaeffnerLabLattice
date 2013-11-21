from PyQt4 import QtGui, QtCore, uic
import os
from common.clients.connection import connection
from twisted.internet.defer import inlineCallbacks

basepath =  os.path.dirname(__file__)
path = os.path.join(basepath, "agilent_E3633A.ui")
base, form = uic.loadUiType(path)

class TextChangingButton(QtGui.QPushButton):
    """Button that changes its text to ON or OFF and colors when it's pressed""" 
    def __init__(self, parent = None):
        super(TextChangingButton, self).__init__(parent)
        self.setCheckable(True)
        self.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=10))
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        #connect signal for appearance changing
        self.toggled.connect(self.setAppearance)
        self.setAppearance(self.isDown())
    
    def set_state_blocking(self, state):
        self.blockSignals(True)
        self.setChecked(state)
        self.blockSignals(False)
        self.setAppearance(state)
    
    def setAppearance(self, down):
        if down:
            self.setText('I')
            self.setPalette(QtGui.QPalette(QtCore.Qt.darkGreen))
        else:
            self.setText('O')
            self.setPalette(QtGui.QPalette(QtCore.Qt.black))
    
    def sizeHint(self):
        return QtCore.QSize(37, 26)

class widget_ui(base, form):
    def __init__(self, parent = None):
        super(widget_ui, self).__init__(parent)
        self.setupUi(self)
        self.button = TextChangingButton()
        self.layout().addWidget(self.button,2,2)

class agilent_E3633A(QtGui.QFrame, widget_ui):
    
    '''
    GPIB device ID should be subclassed by the client
    '''
    GPIB_device_ID = None
    title_text = None
    
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
        yield self.cxn.add_on_connect('Agilent E3633A',self.reinitialize)
        yield self.cxn.add_on_disconnect('Agilent E3633A',self.disable)
    
    @inlineCallbacks
    def initialize_gui(self):
        if self.title_text is not None:
            self.title.setText(self.title_text)
        yield self.populate_gui()
        self.connect_gui()
    
    @inlineCallbacks
    def populate_gui(self):
        server = yield self.cxn.get_server('Agilent E3633A')
        yield server.select_device(self.GPIB_device_ID, context = self.context)
        voltage = yield server.voltage(context = self.context)
        current = yield server.current(context = self.context)
        output = yield server.output(context = self.context)
        self.set_widget_blocking(self.voltage, voltage['V'])
        self.set_widget_blocking(self.current, current['A'])
        self.button.set_state_blocking(output)
    
    def set_widget_blocking(self, widget, value):
        widget.blockSignals(True)
        widget.setValue(value)
        widget.blockSignals(False)
    
    
    def connect_gui(self):
        self.current.valueChanged.connect(self.on_new_current)
        self.voltage.valueChanged.connect(self.on_new_voltage)
        self.button.toggled.connect(self.on_new_output)
    
    @inlineCallbacks
    def on_new_current(self, current):
        server = yield self.cxn.get_server('Agilent E3633A')
        yield server.current(self.WithUnit(current, 'A'), context = self.context)
    
    @inlineCallbacks
    def on_new_voltage(self, voltage):
        server = yield self.cxn.get_server('Agilent E3633A')
        yield server.voltage(self.WithUnit(voltage, 'V'), context = self.context)
    
    @inlineCallbacks
    def on_new_output(self, output):
        server = yield self.cxn.get_server('Agilent E3633A')
        yield server.output(output, context = self.context)
            
    @inlineCallbacks
    def reinitialize(self):
        self.setDisabled(False)
        yield self.populate_gui()
            
    def disable(self):
        self.setDisabled(True)
    
    def closeEvent(self, x):
        self.reactor.stop()
    
class magnet_Control(agilent_E3633A):
    
    GPIB_device_ID = 'lattice-imaging GPIB Bus - GPIB0::5'
    title_text = 'Main Coil'

class oven_Control(agilent_E3633A):
    
    GPIB_device_ID = 'lattice-imaging GPIB Bus - GPIB1::4'
    title_text = 'Oven'
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = oven_Control(reactor)
    widget.show()
    reactor.run()