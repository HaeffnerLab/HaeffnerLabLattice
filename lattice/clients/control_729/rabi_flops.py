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
        layout.addWidget(self.lim, 0, 0, 1, 2)
        layout.addWidget(self.freq, 1, 0, 1, 2)
        label = QtGui.QLabel("Repeat each time")
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter)
        layout.addWidget(label, 2, 0, 1, 1)
        self.repeat = QtGui.QSpinBox()
        self.repeat.setKeyboardTracking(False)
        layout.addWidget(self.repeat, 2, 1, 1, 1)
        self.setLayout(layout)

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
                #integer
                tuple(c.repeatitions_per_time):Parameter(c.repeatitions_per_time, setValueBlocking(self.repeat), self.repeat.valueChanged, self.repeat.setRange, None),
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