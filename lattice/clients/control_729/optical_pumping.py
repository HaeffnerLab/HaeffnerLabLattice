from PyQt4 import QtGui
from helper_widgets import saved_frequencies_dropdown
from twisted.internet.defer import inlineCallbacks
from configuration import config_729_optical_pumping as c


class Parameter(object):
    def __init__(self, path, setValue, updateSignal, setRange = None, units = ''):
        self.path = path
        self.setValue = setValue
        self.setRange = setRange
        self.updateSignal = updateSignal
        self.units = units

class optical_pumping(QtGui.QWidget):
    def __init__(self, reactor, cxn = None, parent=None):
        super(optical_pumping, self).__init__(parent)
        self.reactor = reactor
        self.cxn = cxn
        self.subscribed = False
        self.initializeGUI()
        self.createDict()
        self.connect_labrad()
    
    def createDict(self):
        '''dictionary for tracking relevant setters and getters for all the parameters coming in from semaphore'''
        
        def setValueBlocking(w):
            def func(val):
                w.blockSignals(True)
                w.setValue(val)
                w.blockSignals(False)
            return func
        
        def setValueBlocking_cb(w):
            def func(val):
                w.blockSignals(True)
                w.setChecked(val)
                w.blockSignals(False)
            return func
        
        self.d = {
                #spin boxes
                tuple(c.optical_pumping_amplitude_729): Parameter(c.optical_pumping_amplitude_729, setValueBlocking(self.ampl729), self.ampl729.valueChanged, self.ampl729.setRange, 'dBm'),
                tuple(c.optical_pumping_amplitude_854): Parameter(c.optical_pumping_amplitude_854, setValueBlocking(self.ampl854), self.ampl854.valueChanged, self.ampl854.setRange, 'dBm'),
                tuple(c.optical_pumping_continuous_duration):Parameter(c.optical_pumping_continuous_duration, setValueBlocking(self.cont_729_dur), self.cont_729_dur.valueChanged, self.cont_729_dur.setRange, 'ms'),
                tuple(c.optical_pumping_continuous_pump_additional):Parameter(c.optical_pumping_continuous_pump_additional, setValueBlocking(self.pump_ratio), self.pump_ratio.valueChanged, self.pump_ratio.setRange, 'ms'),
                tuple(c.optical_pumping_frequency):Parameter(c.optical_pumping_frequency, setValueBlocking(self.freq), self.freq.valueChanged, self.freq.setRange, 'MHz'),
                tuple(c.optical_pumping_pulsed_duration_729):Parameter(c.optical_pumping_pulsed_duration_729, setValueBlocking(self.pulse_729), self.pulse_729.valueChanged, self.pulse_729.setRange, 'us'),
                tuple(c.optical_pumping_pulsed_duration_854):Parameter(c.optical_pumping_pulsed_duration_854, setValueBlocking(self.pulse_854), self.pulse_854.valueChanged, self.pulse_854.setRange, 'us'),
                #integer
                tuple(c.optical_pumping_pulsed_cycles):Parameter(c.optical_pumping_pulsed_cycles, setValueBlocking(self.pulses), self.pulses.valueChanged, self.pulses.setRange, ''),
                #bool
                tuple(c.optical_pumping_continuous):Parameter(c.optical_pumping_continuous, setValueBlocking_cb(self.cont_cb), updateSignal = self.cont_cb.toggled),
                tuple(c.optical_pumping_pulsed):Parameter(c.optical_pumping_pulsed, setValueBlocking_cb(self.pulsed_cb), updateSignal = self.pulsed_cb.toggled),
                tuple(c.optical_pumping_enable):Parameter(c.optical_pumping_enable, setValueBlocking_cb(self.enable), updateSignal = self.enable.toggled),
                  }
    
    
    @inlineCallbacks
    def connect_labrad(self):
        from labrad import types as T
        self.T = T
        if self.cxn is None:
            from connection import connection
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            yield self.subscribe_semaphore()
        except Exception, e:
            print 'Not Initially Connected to Semaphore',e
            self.setDisabled(True)
        self.cxn.on_connect['Semaphore'].append( self.reinitialize_semaphore)
        self.cxn.on_disconnect['Semaphore'].append( self.disable)
        self.connect_widgets()

    
    @inlineCallbacks
    def subscribe_semaphore(self): 
        yield self.cxn.servers['Semaphore'].signal__parameter_change(c.ID, context = self.context)
        yield self.cxn.servers['Semaphore'].addListener(listener = self.on_parameter_change, source = None, ID = c.ID, context = self.context)
        for path,param in self.d.iteritems():
            path = list(path)
            init_val = yield self.cxn.servers['Semaphore'].get_parameter(path, context = self.context)
            self.set_value(param, init_val)
        self.subscribed = True
    
    def on_parameter_change(self, x, y):
        path, init_val = y 
        print 'git new param', path, init_val
        if tuple(path) in self.d.keys():
            param = self.d[tuple(path)]
            self.set_value(param, init_val)
    
    @inlineCallbacks
    def reinitialize_semaphore(self):
        self.setDisabled(False)
        yield self.cxn.servers['Semaphore'].signal__parameter_change(c.ID, context = self.context)
        if not self.subscribed:
            yield self.cxn.servers['Semaphore'].addListener(listener = self.on_parameter_change, source = None, ID = c.ID, context = self.context)
            for path,param in self.d.iteritems():
                path = list(path)
                init_val = yield self.cxn.servers['Semaphore'].get_parameter(path, context = self.context)
                self.set_value(param, init_val)
            self.subscribed = True
    
    def set_value(self, param, val):
        if type(val) == bool:
            param.setValue(val)
        else:
            try:
                newval = [v.inUnitsOf(param.units) for v in val]
                val = newval
            except:
                #if unitless number
                pass
            param.setRange(val[0],val[1])
            param.setValue(val[2])
        
    @inlineCallbacks
    def disable(self):
        self.setDisabled(True)
        yield None
    
    def initializeGUI(self):
        self.create_widgets()
        self.create_layout()
    
    def create_widgets(self):
        self.freq = QtGui.QDoubleSpinBox()
        self.freq.setSuffix('MHz')
        self.freq.setDecimals(3)
        self.freq.setSingleStep(0.01)
        self.ampl729 = QtGui.QDoubleSpinBox()
        self.ampl854 = QtGui.QDoubleSpinBox()
        for w in [self.ampl729, self.ampl854]:
            w.setSuffix('dBm')
            w.setDecimals(1)
            w.setSingleStep(0.1)
            w.setKeyboardTracking(False)
        
        self.cont_729_dur = QtGui.QDoubleSpinBox()
        self.pump_ratio = QtGui.QDoubleSpinBox()
        for w in [self.cont_729_dur, self.pump_ratio]:
            w.setKeyboardTracking(False)
            w.setSuffix('ms')
            w.setDecimals(1)
            w.setSingleStep(0.1)
            
        self.pulses = QtGui.QSpinBox()
        self.pulse_729 = QtGui.QDoubleSpinBox()
        self.pulse_854 = QtGui.QDoubleSpinBox()
        for w in [self.pulse_729, self.pulse_854]:
            w.setSuffix('\265s')
            w.setDecimals(1)
            w.setSingleStep(0.1)
            w.setKeyboardTracking(False)
        #make checkboxes
        self.enable = QtGui.QCheckBox()
        self.button_group  = bg = QtGui.QButtonGroup()
        self.cont_cb = QtGui.QRadioButton()
        self.pulsed_cb = QtGui.QRadioButton()
        #make them exclusive
        bg.addButton(self.cont_cb)
        bg.addButton(self.pulsed_cb)
        bg.setExclusive(True)
        self.cont_cb.setChecked(True)
        #make dropdown
        self.dropdown = saved_frequencies_dropdown(self.reactor)
    
    def create_layout(self):
        layout = QtGui.QGridLayout()
        #row1
        frame = QtGui.QFrame()
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QLabel('Enable'))
        hbox.addWidget(self.enable)
        hbox.addWidget(QtGui.QLabel('Frequency'))
        hbox.addWidget(self.freq)
        hbox.addWidget(self.dropdown)
        frame.setLayout(hbox)
        layout.addWidget(frame, 0, 0, 1, 8)
        #row2
        frame = QtGui.QFrame()
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QLabel('Amplitude 729')) 
        hbox.addWidget(self.ampl729) 
        hbox.addWidget(QtGui.QLabel('Amplitude 854')) 
        hbox.addWidget(self.ampl854) 
        frame.setLayout(hbox)
        layout.addWidget(frame, 1, 0, 1, 6)
        #row3
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.Box)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QLabel('Continous'))
        hbox.addWidget(self.cont_cb)
        hbox.addWidget(QtGui.QLabel('Duration'))
        hbox.addWidget(self.cont_729_dur)
        hbox.addWidget(QtGui.QLabel('Additional Repump'))
        hbox.addWidget(self.pump_ratio)
        frame.setLayout(hbox)
        layout.addWidget(frame, 2, 0, 1, 6)
        #row4
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.Box)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QLabel('Pulsed'))
        hbox.addWidget(self.pulsed_cb)
        hbox.addWidget(QtGui.QLabel('Cycles'))
        hbox.addWidget(self.pulses)
        hbox.addWidget(QtGui.QLabel('Duration 729'))
        hbox.addWidget(self.pulse_729)
        hbox.addWidget(QtGui.QLabel('Duration 854'))
        hbox.addWidget(self.pulse_854)
        frame.setLayout(hbox)
        layout.addWidget(frame, 3, 0, 1, 8)
        self.setLayout(layout)
        self.show()
    
    def connect_widgets(self):
        self.dropdown.selected_signal.connect(self.freq.setValue)
        for params in self.d.itervalues():
            params.updateSignal.connect(self.set_labrad_parameter(params.path, params.units))
    
    def set_labrad_parameter(self, path, units):
        @inlineCallbacks
        def func(new_val):
            try:
                if type(new_val) == bool:
                    yield self.cxn.servers['Semaphore'].set_parameter(path, new_val, context = self.context)
                else:
                    new_val = self.T.Value(new_val, units)
                    minim,maxim,cur = yield self.cxn.servers['Semaphore'].get_parameter(path, context = self.context)
                    yield self.cxn.servers['Semaphore'].set_parameter(path, [minim,maxim,new_val], context = self.context)
            except Exception,e:
                print e
        return( func)
        
    def closeEvent(self, x):
        self.reactor.stop()
          
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = optical_pumping(reactor)
    widget.show()
    reactor.run()