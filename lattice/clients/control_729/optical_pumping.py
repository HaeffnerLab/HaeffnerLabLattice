from PyQt4 import QtGui
from helper_widgets import saved_frequencies_dropdown

class optical_pumping_parameters(QtGui.QWidget):
    def __init__(self, reactor, abs_range = (150,250), parent=None):
        super(optical_pumping_parameters, self).__init__(parent)
        self.reactor = reactor
        self.absoluteRange = abs_range
        self.initializeGUI()
        
    def initializeGUI(self):
        self.create_widgets()
        self.create_layout()
        self.connect_widgets()
    
    def create_widgets(self):
        self.freq = QtGui.QDoubleSpinBox()
        self.freq.setRange(*self.absoluteRange)
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
        self.cont_729_dur.setSuffix('ms')
        self.cont_729_dur.setDecimals(1)
        self.cont_729_dur.setSingleStep(0.1)
        for w in [self.cont_729_dur, self.pump_ratio]:
            w.setKeyboardTracking(False)
        
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
        layout.addWidget(QtGui.QLabel('Amplitude 729')) 
        layout.addWidget(self.ampl729) 
        layout.addWidget(QtGui.QLabel('Amplitude 854')) 
        layout.addWidget(self.ampl854) 
        frame.setLayout(hbox)
        layout.addWidget(frame, 1, 2, 1, 6)
        #row3
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.Box)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QLabel('Continous'))
        hbox.addWidget(self.cont_cb)
        hbox.addWidget(QtGui.QLabel('Duration'))
        hbox.addWidget(self.cont_729_dur)
        hbox.addWidget(QtGui.QLabel('Pump Ratio'))
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
    
    def closeEvent(self, x):
        self.reactor.stop()
          
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = optical_pumping_parameters(reactor)
    widget.show()
    reactor.run()