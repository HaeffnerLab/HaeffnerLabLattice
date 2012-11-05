from qtui.QCustomFreqPower import QCustomFreqPower
from twisted.internet.defer import inlineCallbacks
from DDS_CONTROL_config import dds_control_config
from connection import connection
from PyQt4 import QtGui

class RS_CHAN(QCustomFreqPower):
            
    def __init__(self, reactor, device, ip = 'localhost', name = None, parent=None):
        if name is None: name = device
        super(RS_CHAN, self).__init__('RS: {}'.format(name), True, parent)
        self.reactor = reactor
        self.ip = ip
        self.device = device
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad import types as T
        self.T = T
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(self.ip)
        self.server = yield self.cxn.rohdeschwarz_server
        yield self.server.select_device(self.device)
        self.setupWidget()
    
    def followNewSetting(self, x, (kind,value)):
        if kind == 'frequency':
            self.setFreqNoSignal(value)
        elif kind == 'amplitude':
            self.setPowerNoSignal(value)
    
    def followNewState(self, x, checked):
        self.setStateNoSignal(checked)
        
    @inlineCallbacks
    def setupWidget(self):
        #get initial values
        initpower = yield self.server.amplitude()
        initfreq = yield self.server.frequency()
        initstate = yield self.server.output()
        self.spinPower.setValue(initpower)
        self.spinFreq.setValue(initfreq)
        self.buttonSwitch.setChecked(initstate)
        self.setText(initstate)
        #connect functions
        self.spinPower.valueChanged.connect(self.powerChanged)
        self.spinFreq.valueChanged.connect(self.freqChanged) 
        self.buttonSwitch.toggled.connect(self.switchChanged)
        
    @inlineCallbacks
    def powerChanged(self, pwr):
        val = self.T.Value(pwr, 'dBm')
        yield self.server.amplitude(val)
        
    @inlineCallbacks
    def freqChanged(self, freq):
        val = self.T.Value(freq, 'MHz')
        yield self.server.frequency(val)
        
    @inlineCallbacks
    def switchChanged(self, pressed):
        yield self.server.output(pressed)
    
    def closeEvent(self, x):
        self.reactor.stop()  

class RS_CONTROL(QtGui.QWidget):
    def __init__(self, reactor, ip , devices = None):
        super(RS_CONTROL, self).__init__()
        self.reactor = reactor
        self.ip = ip
        self.devices = devices
        self.setupDDS()
        
    @inlineCallbacks
    def setupDDS(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(self.ip)
        self.server = yield self.cxn.rohdeschwarz_server
        allDevices = yield self.server.list_devices()
        allDevices = [dev[1] for dev in allDevices]
        layout = QtGui.QHBoxLayout()
        if self.devices is None:
            self.devices = zip(allDevices,allDevices)
        for dev,name in self.devices:
            if dev in allDevices:
                widget = RS_CHAN(self.reactor, dev, name = name, ip = self.ip)
                layout.addWidget(widget)
        self.setLayout(layout)
    
    def closeEvent(self, x):
        self.reactor.stop()

class RS_CONTROL_LOCAL(RS_CONTROL):
    def __init__(self, reactor):
        ip = '192.168.169.197'
        devices = [('lattice-imaging GPIB Bus - USB0::0x0AAD::0x0054::102549','AxialRF'),('lattice-imaging GPIB Bus - USB0::0x0AAD::0x0054::104543','Axial Beam')]
        super(RS_CONTROL_LOCAL, self).__init__(reactor, ip, devices)
         
class RS_CONTROL_LAB(RS_CONTROL):
    def __init__(self, reactor):
        ip = '192.168.169.49'
        devices = [('lab-49 GPIB Bus - USB0::0x0AAD::0x0054::104542','729DP')]
        super(RS_CONTROL_LAB, self).__init__(reactor, ip, devices)

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    trapdriveWidget = RS_CONTROL_LOCAL(reactor)
    #trapdriveWidget = RS_CONTROL_LAB(reactor)
    trapdriveWidget.show()
    reactor.run()