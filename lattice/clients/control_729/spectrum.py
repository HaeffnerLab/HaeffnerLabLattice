from PyQt4 import QtGui,QtCore
from helper_widgets import durationWdiget, limitsWidget, saved_frequencies_dropdown
from configuration import config_729_spectrum as c
from async_semaphore import async_semaphore, Parameter

class limitWidget_with_dropdown(limitsWidget):
    def __init__(self, reactor):
        super(limitWidget_with_dropdown, self).__init__(reactor, 'MHz')
        layout = self.layout()
        self.dropdown = saved_frequencies_dropdown(self.reactor)
        layout.addWidget(self.dropdown)
        self.dropdown.selected_signal.connect(self.center.setValue)
    

class spectrum(QtGui.QWidget):
    
    max_segments = 3
    new_frequencies_signal = QtCore.pyqtSignal(list)
    
    def __init__(self, reactor, parent=None):
        super(spectrum, self).__init__(parent)
        self.reactor = reactor
        self.initializeGUI()
        self.connect_widgets()
        #start with one segment shown
        self.segments.setCurrentIndex(0)
        self.on_new_index(0)
        
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        self.segments = QtGui.QComboBox()
        self.segments.addItems([str(i + 1) for i in range(self.max_segments)])
        self.duration = durationWdiget(self.reactor)
        layout.addWidget(self.duration, 0, 0, 2, 2)
        self.heating = QtGui.QDoubleSpinBox()
        self.heating.setKeyboardTracking(False)
        self.heating.setSuffix('ms')
        self.repeats = QtGui.QSpinBox()
        self.repeats.setKeyboardTracking(False)
        label = QtGui.QLabel("Repeat each frequency")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)      
        layout.addWidget(label, 2, 0, 1, 1)
        layout.addWidget(self.repeats, 2, 1, 1, 1)
        label = QtGui.QLabel("Heating")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)      
        layout.addWidget(label, 2, 2, 1, 1)
        layout.addWidget(self.heating, 2, 3, 1, 1)
        label = QtGui.QLabel("Segments")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 0, 2, 1, 1)
        layout.addWidget(self.segments, 0, 3, 1, 1)
        self.limitWidgets = [limitWidget_with_dropdown(self.reactor) for i in range(self.max_segments)]
        for index,w in enumerate(self.limitWidgets):
            layout.addWidget(w, index + 3, 0, 1, 4)
            w.displayed = None
        self.setLayout(layout)
    
    def connect_widgets(self):
        self.segments.currentIndexChanged.connect(self.on_new_index)
        for w in self.limitWidgets:
            w.new_list_signal.connect(self.emit_new)
    
    def emit_new(self):
        freqs = []
        shownWidgets = [w for w in self.limitWidgets if w.displayed]
        for w in shownWidgets:
            freqs.extend(w.frequencies)
        self.new_frequencies_signal.emit(freqs)
    
    
    def on_new_index(self, index):
        index = index + 1
        for i in range(0, self.max_segments):
            self.limitWidgets[i].displayed = True
            self.limitWidgets[i].show()
        for i in range(index, self.max_segments):
            self.limitWidgets[i].displayed = False
            self.limitWidgets[i].hide()
        
    def closeEvent(self, x):
        self.reactor.stop()
        
class spectrum_connection(spectrum, async_semaphore):
    
    def __init__(self, reactor, cxn = None, parent = None):
        super(spectrum_connection, self).__init__(reactor)
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
                tuple(c.excitation_time): Parameter(c.excitation_time, self.duration.setNewDuration_blocking, self.duration.new_duration, self.duration.duration.setRange, 'us'),
                tuple(c.heating_time): Parameter(c.heating_time, setValueBlocking(self.heating), self.heating.valueChanged, self.heating.setRange, 'ms'),
                #integer
                tuple(c.repeatitions_per_frequency):Parameter(c.repeatitions_per_frequency, setValueBlocking(self.repeats), self.repeats.valueChanged, self.repeats.setRange, ''),
                #list
                tuple(c.frequencies):Parameter(c.frequencies, do_nothing, self.new_frequencies_signal, self.on_new_freq_range, 'MHz'),
                  }
    
    def on_new_freq_range(self, minim,maxim):
        for w in self.limitWidgets:
            w.setRange(minim,maxim)
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = spectrum_connection(reactor)
    widget.show()
    reactor.run()