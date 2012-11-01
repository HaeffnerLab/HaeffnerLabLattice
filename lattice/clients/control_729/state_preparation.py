from PyQt4 import QtGui, QtCore
from configuration import config_729_general_parameters as c
from async_semaphore import async_semaphore, Parameter

class state_preparation(QtGui.QWidget):
    def __init__(self, reactor, cxn = None, parent = None):
        super(state_preparation, self).__init__(parent)
        self.reactor = reactor
        self.font = QtGui.QFont('MS Shell Dlg 2',pointSize=12)
        self.large_font = QtGui.QFont('MS Shell Dlg 2',pointSize=14)
        self.initializeGUI()
    
    def initializeGUI(self):
        repump_d_frame = self.make_repump_d_frame()
        heating_frame = self.make_heating_frame()
        doppler_cooling_frame = self.make_doppler_cooling_frame()
        widgetLayout = QtGui.QVBoxLayout()
        widgetLayout.addWidget(repump_d_frame)
        widgetLayout.addWidget(doppler_cooling_frame)
        widgetLayout.addWidget(heating_frame)
        self.setLayout(widgetLayout)
    
    def make_doppler_cooling_frame(self):
        frame = QtGui.QFrame()
        frame.setFrameStyle(QtGui.QFrame.Panel  | QtGui.QFrame.Sunken)
        frame.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        layout = QtGui.QGridLayout()
        self.doppler_duration = QtGui.QDoubleSpinBox()
        self.doppler_duration.setSuffix('ms')
        self.doppler_duration_additional = QtGui.QDoubleSpinBox()
        for w in [self.doppler_duration, self.doppler_duration_additional]:
            w.setKeyboardTracking(False)
            w.setFont(self.font)
            w.setDecimals(1)
        self.doppler_duration_additional.setSuffix('\265s')
        self.doppler_amplitude_397 = QtGui.QDoubleSpinBox()
        self.doppler_amplitude_866 = QtGui.QDoubleSpinBox()
        self.doppler_frequency_866 = QtGui.QDoubleSpinBox()
        self.doppler_frequency_397 = QtGui.QDoubleSpinBox()
        for w in [self.doppler_amplitude_866, self.doppler_amplitude_397]:
            w.setSuffix('dBm')
            w.setDecimals(1)
            w.setSingleStep(0.1)
            w.setKeyboardTracking(False)
            w.setFont(self.font)
        for w in [self.doppler_frequency_397, self.doppler_frequency_866]:
            w.setKeyboardTracking(False)
            w.setSuffix('MHz')
            w.setDecimals(1)
            w.setFont(self.font)
        label = QtGui.QLabel("Doppler Cooling", font = self.large_font)
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)      
        layout.addWidget(label, 0, 0, 1, 2)
        label = QtGui.QLabel("Duration", font = self.font)
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 0, 2)
        layout.addWidget(self.doppler_duration, 0, 3)
        label = QtGui.QLabel("Frequency 397", font = self.font)
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 1, 0)
        layout.addWidget(self.doppler_frequency_397, 1, 1)
        label = QtGui.QLabel("Amplitude 397", font = self.font)
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 1, 2)
        layout.addWidget(self.doppler_amplitude_397, 1, 3)
        label = QtGui.QLabel("Frequency 866", font = self.font)
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 2, 0)
        layout.addWidget(self.doppler_frequency_866, 2, 1)
        label = QtGui.QLabel("Amplitude 866", font = self.font)
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 2, 2)
        layout.addWidget(self.doppler_amplitude_866, 2, 3)
        label = QtGui.QLabel("Extended 866 Repump", font = self.font)
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 3, 2)
        layout.addWidget(self.doppler_duration_additional, 3, 3)
        
        frame.setLayout(layout)
        return frame
        
    def make_heating_frame(self):
        frame = QtGui.QFrame()
        frame.setFrameStyle(QtGui.QFrame.Panel  | QtGui.QFrame.Sunken)
        frame.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        layout = QtGui.QGridLayout()
        self.heating = QtGui.QDoubleSpinBox()
        self.heating.setKeyboardTracking(False)
        self.heating.setSuffix('ms')
        self.heating.setFont(self.font)
        label = QtGui.QLabel("Background Heating", font = self.large_font)
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)      
        layout.addWidget(label, 0, 0, 1, 2)
        label = QtGui.QLabel("Duration", font = self.font)
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 0, 2)
        layout.addWidget(self.heating, 0, 3)
        frame.setLayout(layout)
        return frame
    
    def make_repump_d_frame(self):
        #repump D
        self.repump_d_duration = QtGui.QDoubleSpinBox()
        self.repump_d_duration.setSuffix('\265s')
        self.repump_d_duration.setKeyboardTracking(False)
        self.repump_d_duration.setFont(self.font)
        self.repump_d_duration.setDecimals(1)
        #amplitudes
        self.ampl_854 = QtGui.QDoubleSpinBox()
        self.freq_854 = QtGui.QDoubleSpinBox()
        for w in [self.ampl_854]:
            w.setSuffix('dBm')
            w.setDecimals(1)
            w.setSingleStep(0.1)
            w.setKeyboardTracking(False)
            w.setFont(self.font)
        for w in [self.freq_854]:
            w.setKeyboardTracking(False)
            w.setSuffix('MHz')
            w.setDecimals(1)
            w.setFont(self.font)
        #repump d layout
        frame = QtGui.QFrame()
        frame.setFrameStyle(QtGui.QFrame.Panel  | QtGui.QFrame.Sunken)
        frame.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        layout = QtGui.QGridLayout()
        title = QtGui.QLabel("Repump D5/2", font = self.large_font)
        title.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        layout.addWidget(title, 0, 0, 1, 2)
        label = QtGui.QLabel("Amplitude 854", font = self.font)
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 1, 2)
        layout.addWidget(self.ampl_854, 1, 3)
        label = QtGui.QLabel("Frequency 854", font = self.font)
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 1, 0)
        layout.addWidget(self.freq_854, 1, 1)
        label = QtGui.QLabel("Duration", font = self.font)
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 0, 2)
        layout.addWidget(self.repump_d_duration, 0, 3)
        frame.setLayout(layout)
        return frame

    def closeEvent(self, x):
        self.reactor.stop()

class state_preparation_connection(state_preparation, async_semaphore):
    
    def __init__(self, reactor, cxn = None, parent = None):
        super(state_preparation_connection, self).__init__(reactor)
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
#                tuple(c.amplitude_854): Parameter(c.amplitude_854, setValueBlocking(self.ampl_854), self.ampl_854.valueChanged, self.ampl_854.setRange, 'dBm'),
#                tuple(c.heating_duration): Parameter(c.heating_duration, setValueBlocking(self.heating), self.heating.valueChanged, self.heating.setRange, 'ms'),
#                tuple(c.repump_d_duration): Parameter(c.repump_d_duration, setValueBlocking(self.repump_d_duration), self.repump_d_duration.valueChanged, self.repump_d_duration.setRange, 'ms'),
#                tuple(c.state_readout_frequency_397): Parameter(c.state_readout_frequency_397, setValueBlocking(self.state_readout_frequency_397), self.state_readout_frequency_397.valueChanged, self.state_readout_frequency_397.setRange, 'MHz'),
#                tuple(c.state_readout_amplitude_397): Parameter(c.state_readout_amplitude_397, setValueBlocking(self.state_readout_amplitude_397), self.state_readout_amplitude_397.valueChanged, self.state_readout_amplitude_397.setRange, 'dBm'),      
               }

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = state_preparation_connection(reactor)
    widget.show()
    reactor.run()