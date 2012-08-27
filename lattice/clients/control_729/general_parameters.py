from PyQt4 import QtGui, QtCore
from configuration import config_729_general_parameters as c
from async_semaphore import async_semaphore, Parameter

class general_parameters(QtGui.QWidget):
    def __init__(self, reactor, cxn = None, parent = None):
        super(general_parameters, self).__init__(parent)
        self.reactor = reactor
        self.initializeGUI()
    
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        #repeats
        self.repeats = QtGui.QSpinBox()
        self.repeats.setKeyboardTracking(False)
        label = QtGui.QLabel("Repeat each point")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)      
        layout.addWidget(label, 0, 0, 1, 1)
        layout.addWidget(self.repeats, 0, 1, 1, 1)
        #heating
        self.heating = QtGui.QDoubleSpinBox()
        self.heating.setKeyboardTracking(False)
        self.heating.setSuffix('ms')
        self.repump_d_duration = QtGui.QDoubleSpinBox()
        self.repump_d_duration.setSuffix('ms')
        self.repump_d_duration.setKeyboardTracking(False)
        label = QtGui.QLabel("Heating")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)      
        layout.addWidget(label, 1, 0, 1, 1)
        layout.addWidget(self.heating, 1, 1, 1, 1)
        #amplitudes
        self.ampl_854 = QtGui.QDoubleSpinBox()
        self.state_readout_amplitude_397 = QtGui.QDoubleSpinBox()

        for w in [self.ampl_854, self.state_readout_amplitude_397]:
            w.setSuffix('dBm')
            w.setDecimals(1)
            w.setSingleStep(0.1)
            w.setKeyboardTracking(False)
        #staet readout frequency 397
        self.state_readout_frequency_397 = QtGui.QDoubleSpinBox()
        self.state_readout_frequency_397.setKeyboardTracking(False)
        self.state_readout_frequency_397.setSuffix('MHz')
        self.state_readout_frequency_397.setDecimals(1)

        label = QtGui.QLabel("Repump D Amplitude 854")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 4, 0, 1, 1)
        layout.addWidget(self.ampl_854, 4, 1, 1, 1)
        label = QtGui.QLabel("Repump D Duration")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 4, 2, 1, 1)
        layout.addWidget(self.repump_d_duration, 4, 3, 1, 1)
        label = QtGui.QLabel("State Readout Frequency 397")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 5, 0, 1, 1)
        layout.addWidget(self.state_readout_frequency_397, 5, 1, 1, 1)
        label = QtGui.QLabel("State Readout Amplitude 397")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 5, 2, 1, 1)
        layout.addWidget(self.state_readout_amplitude_397, 5, 3, 1, 1)
        
        
        self.setLayout(layout)
    
    def closeEvent(self, x):
        self.reactor.stop()

class general_parameters_connection(general_parameters, async_semaphore):
    
    def __init__(self, reactor, cxn = None, parent = None):
        super(general_parameters_connection, self).__init__(reactor)
        self.subscribed = False
        self.cxn = cxn
        self.createDict()
        self.semaphoreID = c.ID
        self.connect_labrad()
        
    def createDict(self):
        '''dictionary for tracking relevant setters and getters for all the parameters coming in from semaphore'''
        def setValueBlocking(w):
            def func(val):
                w.blockSignals(True)
                w.setValue(val)
                w.blockSignals(False)
            return func
        
        def do_nothing(*args):
            pass
        
        self.d = {
                #spin boxes
                tuple(c.amplitude_854): Parameter(c.amplitude_854, setValueBlocking(self.ampl_854), self.ampl_854.valueChanged, self.ampl_854.setRange, 'dBm'),
                tuple(c.heating_duration): Parameter(c.heating_duration, setValueBlocking(self.heating), self.heating.valueChanged, self.heating.setRange, 'ms'),
                tuple(c.repump_d_duration): Parameter(c.repump_d_duration, setValueBlocking(self.repump_d_duration), self.repump_d_duration.valueChanged, self.repump_d_duration.setRange, 'ms'),
                tuple(c.state_readout_frequency_397): Parameter(c.state_readout_frequency_397, setValueBlocking(self.state_readout_frequency_397), self.state_readout_frequency_397.valueChanged, self.state_readout_frequency_397.setRange, 'MHz'),
                tuple(c.state_readout_amplitude_397): Parameter(c.state_readout_amplitude_397, setValueBlocking(self.state_readout_amplitude_397), self.state_readout_amplitude_397.valueChanged, self.state_readout_amplitude_397.setRange, 'dBm'),
                #int
                tuple(c.repeat_each_measurement): Parameter(c.repeat_each_measurement, setValueBlocking(self.repeats), self.repeats.valueChanged, self.repeats.setRange, None),
               }

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = general_parameters_connection(reactor)
    widget.show()
    reactor.run()