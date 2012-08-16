from PyQt4 import QtGui,QtCore
from helper_widgets import durationWdiget, limitsWidget, saved_frequencies_dropdown
from twisted.internet.defer import inlineCallbacks

class limitWidget_with_dropdown(limitsWidget):
    def __init__(self, reactor):
        super(limitWidget_with_dropdown, self).__init__(reactor)
        layout = self.layout()
        self.dropdown = saved_frequencies_dropdown(self.reactor)
        layout.addWidget(self.dropdown)
        self.dropdown.selected_signal.connect(self.center.setValue)
    

class spectrum(QtGui.QWidget):
    
    max_segments = 3
    
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
        layout.addWidget(self.duration, 0, 0, 1, 1)
        self.heating = QtGui.QDoubleSpinBox()
        self.heating.setKeyboardTracking(False)
        self.heating.setSuffix('ms')
        label = QtGui.QLabel("Heating")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)      
        layout.addWidget(label, 0, 1, 1, 1)
        layout.addWidget(self.heating, 0, 2, 1, 1)
        label = QtGui.QLabel("Segments")
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        layout.addWidget(label, 1, 1, 1, 1)
        layout.addWidget(self.segments, 1, 2, 1, 1)
        self.limitWidgets = [limitWidget_with_dropdown(self.reactor) for i in range(self.max_segments)]
        for index,w in enumerate(self.limitWidgets):
            layout.addWidget(w, index + 2, 0, 1, 3)
            w.displayed = None
        self.setLayout(layout)
    
    def connect_widgets(self):
        self.segments.currentIndexChanged.connect(self.on_new_index)
        for w in self.limitWidgets:
            w.new_frequencies_signal.connect(self.on_new_frequencies)
    
    def on_new_index(self, index):
        index = index + 1
        for i in range(0, self.max_segments):
            self.limitWidgets[i].displayed = True
            self.limitWidgets[i].show()
        for i in range(index, self.max_segments):
            self.limitWidgets[i].displayed = False
            self.limitWidgets[i].hide()
    
    def on_new_frequencies(self):
        freqs = []
        shownWidgets = [w for w in self.limitWidgets if w.displayed]
        for w in shownWidgets:
            freqs.extend(w.frequencies)
        print freqs
        
    def closeEvent(self, x):
        self.reactor.stop()
        
class spectrum_connection(spectrum):
    def __init__(self, reactor, cxn = None, parent = None):
        super(spectrum_connection, self).__init__(reactor)
        self.cxn = cxn
        self.connect_labrad()
    
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
        self.connect_widgets_labrad()
        
    @inlineCallbacks
    def disable(self):
        self.setDisabled(True)
        yield None
    
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

    
    
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = spectrum_connection(reactor)
    widget.show()
    reactor.run()