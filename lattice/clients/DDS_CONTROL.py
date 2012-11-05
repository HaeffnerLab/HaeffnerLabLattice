from qtui.QCustomFreqPower import QCustomFreqPower
from twisted.internet.defer import inlineCallbacks
from DDS_CONTROL_config import dds_control_config
from connection import connection
from PyQt4 import QtGui

class DDS_CHAN(QCustomFreqPower):
    def __init__(self, chan, reactor, server, parent=None):
        super(DDS_CHAN, self).__init__('DDS: {}'.format(chan), True, parent)
        self.reactor = reactor
        self.chan = chan
        self.server = server
        self.import_labrad()
        
    def import_labrad(self):
        from labrad import types as T
        self.T = T
        self.setupWidget()

    @inlineCallbacks
    def setupWidget(self):
        #get ranges
        MinPower,MaxPower = yield self.server.get_dds_amplitude_range(self.chan)
        MinFreq,MaxFreq = yield self.server.get_dds_frequency_range(self.chan)
        self.setPowerRange((MinPower,MaxPower))
        self.setFreqRange((MinFreq,MaxFreq))
        #get initial values
        initpower = yield self.server.amplitude(self.chan)
        initfreq = yield self.server.frequency(self.chan)
        initstate = yield self.server.output(self.chan)
        self.setStateNoSignal(initstate)
        self.setPowerNoSignal(initpower)
        self.setFreqNoSignal(initfreq)
        #connect functions
        self.spinPower.valueChanged.connect(self.powerChanged)
        self.spinFreq.valueChanged.connect(self.freqChanged) 
        self.buttonSwitch.toggled.connect(self.switchChanged)
    
    def setParamNoSignal(self, param, value):
        if param == 'amplitude':
            self.setPowerNoSignal(value)
        elif param == 'frequency':
            self.setFreqNoSignal(value)
        elif param == 'state':
            self.setStateNoSignal(value)
        
    @inlineCallbacks
    def powerChanged(self, pwr):
        val = self.T.Value(pwr, 'dBm')
        yield self.server.amplitude(self.chan, val)
        
    @inlineCallbacks
    def freqChanged(self, freq):
        print freq
        val = self.T.Value(freq, 'MHz')
        yield self.server.frequency(self.chan, val)
    
    @inlineCallbacks
    def switchChanged(self, pressed):
        yield self.server.output(self.chan,pressed)

    def closeEvent(self, x):
        self.reactor.stop()

class DDS_CONTROL(QtGui.QWidget):
    
    SIGNALID = 319182
    
    def __init__(self, reactor):
        super(DDS_CONTROL, self).__init__()
        self.reactor = reactor
        self.channels = dds_control_config.channels
        self.widgets_per_row = dds_control_config.widgets_per_row
        self.widgets = {}.fromkeys(self.channels)
        self.initialized = False
        self.setupDDS()
        
    @inlineCallbacks
    def setupDDS(self):
        self.cxn = connection()
        yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            yield self.initialize()
        except Exception, e:
            print e
            print 'Pulser not available'
            self.setDisabled(True)
        self.cxn.on_connect['Pulser'].append( self.reinitialize)
        self.cxn.on_disconnect['Pulser'].append( self.disable)
     
    @inlineCallbacks
    def initialize(self):
        server = self.cxn.servers['Pulser']
        yield server.signal__new_dds_parameter(self.SIGNALID)
        yield server.addListener(listener = self.followSignal, source = None, ID = self.SIGNALID)
        yield self.do_layout(server)
        self.initialized = True
    
    @inlineCallbacks
    def reinitialize(self):
        self.setDisabled(False)
        server = self.cxn.servers['Pulser']
        if not self.initialized:
            yield server.signal__new_dds_parameter(self.SIGNALID)
            yield server.addListener(listener = self.followSignal, source = None, ID = self.SIGNALID)
            yield self.do_layout(server)
            self.initialized = True
        else:
            #update any changes in the parameters
            yield server.signal__new_dds_parameter(self.SIGNALID)
            for w in self.widgets.values():
                yield w.setupWidget()
            
    
    @inlineCallbacks
    def do_layout(self, server):
        allChannels = yield server.get_dds_channels()
        layout = QtGui.QGridLayout()
        item = 0
        for chan in self.channels:
            if chan in allChannels:
                widget = DDS_CHAN(chan, self.reactor, server)
                self.widgets[chan] = widget
                layout.addWidget(widget, item // self.widgets_per_row, item % self.widgets_per_row)
                item += 1
        self.setLayout(layout)
        
    
    @inlineCallbacks
    def disable(self):
        self.setDisabled(True)
        yield None
    
    def followSignal(self, x, y):
        chan, param, val = y
        w = self.widgets[chan]
        w.setParamNoSignal(param, val)

    def closeEvent(self, x):
        self.reactor.stop()
        
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
    trapdriveWidget = DDS_CONTROL(reactor)
    #trapdriveWidget = RS_CONTROL_LOCAL(reactor)
    #trapdriveWidget = RS_CONTROL_LAB(reactor)
    trapdriveWidget.show()
    reactor.run()