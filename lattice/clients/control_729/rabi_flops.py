from PyQt4 import QtGui, QtCore
from configuration import config_729_rabi_flop as c
from async_semaphore import async_semaphore, Parameter
from helper_widgets import frequency_wth_dropdown, limitsWidget

class rabi_flop(QtGui.QWidget):
    def __init__(self, reactor, cxn = None, parent = None):
        super(rabi_flop, self).__init__(parent)
        self.reactor = reactor
        self.initializeGUI()
    
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        self.lim = limitsWidget(self.reactor, '\265s')
        self.freq = frequency_wth_dropdown(self.reactor)
        layout.addWidget(self.lim, 1, 0, 1, 2)
        layout.addWidget(self.freq, 2, 0, 1, 2)
        self.ampl_729 = QtGui.QDoubleSpinBox()
        self.ampl_729.setSuffix('dBm')
        self.ampl_729.setDecimals(1)
        self.ampl_729.setSingleStep(0.1)
        self.ampl_729.setKeyboardTracking(False)
        label = QtGui.QLabel("Rabi Amplitude 729")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 0, 0, 1, 1)
        layout.addWidget(self.ampl_729, 0, 1, 1, 1)
        self.setLayout(layout)
    
    def closeEvent(self, x):
        self.reactor.stop()

class rabi_flop_connection(rabi_flop, async_semaphore):
    
    def __init__(self, reactor, cxn = None, parent = None):
        super(rabi_flop_connection, self).__init__(reactor)
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
                tuple(c.frequency): Parameter(c.frequency, setValueBlocking(self.freq.freq), self.freq.freq.valueChanged, self.freq.freq.setRange, 'MHz'),
                tuple(c.rabi_amplitude_729): Parameter(c.rabi_amplitude_729, setValueBlocking(self.ampl_729), self.ampl_729.valueChanged, self.ampl_729.setRange, 'dBm'),
                #list
                tuple(c.excitation_times):Parameter(c.excitation_times, do_nothing, self.lim.new_list_signal, self.lim.setRange, 'us'),
                  }

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = rabi_flop_connection(reactor)
    widget.show()
    reactor.run()