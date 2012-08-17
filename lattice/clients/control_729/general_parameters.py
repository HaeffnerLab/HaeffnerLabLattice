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
        label = QtGui.QLabel("Heating")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)      
        layout.addWidget(label, 1, 0, 1, 1)
        layout.addWidget(self.heating, 1, 1, 1, 1)
        #amplitudes
        self.ampl_729 = QtGui.QDoubleSpinBox()
        self.ampl_854 = QtGui.QDoubleSpinBox()
        self.ampl729_reduction = QtGui.QDoubleSpinBox()
        for w in [self.ampl_729, self.ampl_854, self.ampl729_reduction]:
            w.setSuffix('dBm')
            w.setDecimals(1)
            w.setSingleStep(0.1)
            w.setKeyboardTracking(False)
        label = QtGui.QLabel("Amplitude 729")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 2, 0, 1, 1)
        layout.addWidget(self.ampl_729, 2, 1, 1, 1)
        label = QtGui.QLabel("Amplitude 854")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 2, 2, 1, 1)
        layout.addWidget(self.ampl_854, 2, 3, 1, 1)
        #double pass calibration
        label = QtGui.QLabel("Use Double Pass Calibration")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.enable_calibration = QtGui.QCheckBox()  
        layout.addWidget(label, 3, 0, 1, 1)
        layout.addWidget(self.enable_calibration, 3, 1, 1, 1)
        label = QtGui.QLabel("Calbrated Amplitude Reduction")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)    
        layout.addWidget(label, 3, 2, 1, 1)
        layout.addWidget(self.ampl729_reduction, 3, 3, 1, 1)
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
                tuple(c.amplitude_729): Parameter(c.amplitude_729, setValueBlocking(self.ampl_729), self.ampl_729.valueChanged, self.ampl_729.setRange, 'dBm'),
                tuple(c.amplitude_854): Parameter(c.amplitude_729, setValueBlocking(self.ampl_854), self.ampl_854.valueChanged, self.ampl_854.setRange, 'dBm'),
                tuple(c.calibration_reduction): Parameter(c.calibration_reduction, setValueBlocking(self.ampl729_reduction), self.ampl729_reduction.valueChanged, self.ampl729_reduction.setRange, 'dBm'),
                tuple(c.heating_duration): Parameter(c.heating_duration, setValueBlocking(self.heating), self.heating.valueChanged, self.heating.setRange, 'ms'),
                #int
                tuple(c.repeat_each_measurement): Parameter(c.repeat_each_measurement, setValueBlocking(self.repeats), self.repeats.valueChanged, self.repeats.setRange, None),
                #bool
                tuple(c.enable_calibration): Parameter(c.enable_calibration, self.enable_calibration.setChecked, updateSignal = self.enable_calibration.toggled),
                  }

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = general_parameters_connection(reactor)
    widget.show()
    reactor.run()