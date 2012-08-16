from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
import numpy
from configuration import config_729_hist as c

class readout_histgram(QtGui.QWidget):
    def __init__(self, reactor, cxn = None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.reactor = reactor
        self.cxn = cxn
        self.thresholdVal = None
        self.last_data = None
        self.last_hist = None
        self.subscribed = [False,False]
        self.create_layout()
        self.connect_labrad()
    
    def create_layout(self):
        layout = QtGui.QGridLayout()
        plot_layout = self.create_plot_layout()
        layout.addLayout(plot_layout, 0, 0, 1, 4)
        thresholdLabel = QtGui.QLabel("Threshold (Photon Counts Per Readout)")
        readoutTimeLabel = QtGui.QLabel("Readout Time")
        for l in [thresholdLabel, readoutTimeLabel]:
            l.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.threshold = QtGui.QSpinBox()
        self.threshold.setKeyboardTracking(False)
        self.readout_time = QtGui.QDoubleSpinBox()
        self.readout_time.setKeyboardTracking(False)
        self.readout_time.setSuffix('ms')
        self.readout_time.setDecimals(1)
        self.readout_time.setSingleStep(0.1)
        layout.addWidget(thresholdLabel, 1, 0)
        layout.addWidget(self.threshold, 1, 1)
        layout.addWidget(readoutTimeLabel, 1, 2)
        layout.addWidget(self.readout_time, 1, 3)
        self.setLayout(layout)
   
    def create_plot_layout(self):
        layout = QtGui.QVBoxLayout()
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_xlim([0,100])
        self.thresholdLine = self.axes.axvline(self.thresholdVal, linewidth=3.0, color = 'r', label = 'Threshold')
        self.axes.legend(loc = 'best')
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.mpl_toolbar)
        layout.addWidget(self.canvas)
        return layout
    
    def connect_layout(self):
        self.threshold.valueChanged.connect(self.thresholdChange)
        self.canvas.mpl_connect('button_press_event', self.on_key_press)
        self.readout_time.valueChanged.connect(self.readoutChange)
    
    def on_key_press(self, event):
        if event.button == 2:
            xval = int(round(event.xdata))
            self.threshold.setValue(xval)
    
    def on_new_data(self, readout):
        self.last_data = readout
        self.updade_histogram(readout)
    
    def updade_histogram(self, data):
        #remove old histogram
        if self.last_hist is not None: 
            for obj in self.last_hist: obj.remove()
        self.last_hist = self.axes.bar(data[:,0], data[:,1], width = numpy.max(data[:,0])/len(data[:,0]))
        self.canvas.draw()
    
    @inlineCallbacks
    def thresholdChange(self, threshold):
        #update canvas
        self.update_canvas_line(threshold)
        try:
            minim,maxim,cur = yield self.cxn.servers['Semaphore'].get_parameter(c.readout_threshold_dir, context = self.context)
            yield self.cxn.servers['Semaphore'].set_parameter(c.readout_threshold_dir, [minim,maxim,float(threshold)], context = self.context)
        except Exception:
            yield None
    
    @inlineCallbacks
    def readoutChange(self, value):
        value = self.T.Value(value, 'ms')
        try:
            minim,maxim,cur = yield self.cxn.servers['Semaphore'].get_parameter(c.readout_time_dir, context = self.context)
            yield self.cxn.servers['Semaphore'].set_parameter(c.readout_time_dir, [minim,maxim, value], context = self.context)
        except Exception, e:
            yield None
            
    def update_canvas_line(self, threshold):
        self.thresholdLine.remove()
        self.thresholdLine = self.axes.axvline(threshold, ymin=0, ymax= 200, linewidth=3.0, color = 'r', label = 'Threshold')
        self.canvas.draw()
    
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
            yield self.subscribe_data_vault()
        except Exception:
            self.setDisabled(True)
        try:
            yield self.subscribe_semaphore()
        except Exception, e:
            print 'Not Initially Connected to Semaphore', e
            self.setDisabled(True)
        self.cxn.on_connect['Data Vault'].append( self.reinitialize_data_vault)
        self.cxn.on_connect['Semaphore'].append( self.reinitialize_semaphore)
        self.cxn.on_disconnect['Data Vault'].append( self.disable)
        self.cxn.on_disconnect['Semaphore'].append( self.disable)
        self.connect_layout()
        
    @inlineCallbacks
    def subscribe_data_vault(self):
        yield self.cxn.servers['Data Vault'].signal__new_parameter_dataset(c.ID_A, context = self.context)
        yield self.cxn.servers['Data Vault'].addListener(listener = self.on_new_dataset, source = None, ID = c.ID_A, context = self.context)
        self.subscribed[0] = True
    
    @inlineCallbacks
    def subscribe_semaphore(self): 
        yield self.cxn.servers['Semaphore'].signal__parameter_change(c.ID_B, context = self.context)
        yield self.cxn.servers['Semaphore'].addListener(listener = self.on_parameter_change, source = None, ID = c.ID_B, context = self.context)
        init_val = yield self.cxn.servers['Semaphore'].get_parameter(c.readout_threshold_dir, context = self.context)
        self.threshold.setRange(init_val[0],init_val[1])
        self.threshold.setValue(init_val[2])
        self.update_canvas_line(init_val[2])
        init_val = yield self.cxn.servers['Semaphore'].get_parameter(c.readout_time_dir, context = self.context)
        self.readout_time.setRange( init_val[0].inUnitsOf('ms'),init_val[1].inUnitsOf('ms'))
        self.set_readout_time_block_signals(init_val[2].inUnitsOf('ms'))
        self.subscribed[1] = True
    
    @inlineCallbacks
    def reinitialize_data_vault(self):
        self.setDisabled(False)
        yield self.cxn.servers['Data Vault'].signal__new_parameter_dataset(c.ID_A, context = self.context)
        if not self.subscribed[0]:
            yield self.cxn.servers['Data Vault'].addListener(listener = self.on_new_dataset, source = None, ID = c.ID_A, context = self.context)
            self.subscribed[0] = True
            
    @inlineCallbacks
    def reinitialize_semaphore(self):
        self.setDisabled(False)
        yield self.cxn.servers['Semaphore'].signal__parameter_change(c.ID_B, context = self.context)
        if not self.subscribed[1]:
            yield self.cxn.servers['Semaphore'].addListener(listener = self.on_parameter_change, source = None, ID = c.ID_B, context = self.context)
            self.subscribed[1] = True
        init_val = yield self.cxn.servers['Semaphore'].get_parameter(c.readout_threshold_dir, context = self.context)
        self.threshold.setRange(init_val[0],init_val[1])
        self.set_threshold_block_signals(init_val[2])
        init_val = yield self.cxn.servers['Semaphore'].get_parameter(c.readout_time_dir, context = self.context)
        self.readout_time.setRange( init_val[0].inUnitsOf('ms'),init_val[1].inUnitsOf('ms'))
        self.set_readout_time_block_signals(init_val[2].inUnitsOf('ms'))
        
        
    @inlineCallbacks
    def disable(self):
        self.setDisabled(True)
        yield None
    
    @inlineCallbacks
    def on_parameter_change(self, x, y):
        print 'on par change', x , y
        d, sett = y
        print d, sett
        if d == c.readout_threshold_dir:
            val = sett[2]
            yield deferToThread(self.set_threshold_block_signals, val)
        elif d == c.readout_time_dir:
            val = sett[2]
            yield deferToThread(self.set_readout_time_block_signals, val.inUnitsOf('ms'))
    
    def set_threshold_block_signals(self, thresh):
        self.threshold.blockSignals(True)
        self.threshold.setValue(thresh)
        self.threshold.blockSignals(False)
        self.update_canvas_line(thresh)
    
    def set_readout_time_block_signals(self, val):
        self.readout_time.blockSignals(True)
        self.readout_time.setValue(val)
        self.readout_time.blockSignals(False)
        
    @inlineCallbacks
    def on_new_dataset(self, x, y):
        if y[3] == c.dv_parameter:
            dataset = y[0]
            directory = y[2]
            yield self.cxn.servers['Data Vault'].cd(directory, context = self.context)
            yield self.cxn.servers['Data Vault'].open(dataset, context = self.context)
            data = yield self.cxn.servers['Data Vault'].get( context = self.context)
            data = data.asarray
            yield deferToThread(self.on_new_data, data)
            yield self.cxn.servers['Data Vault'].cd([''], context = self.context)
                                          
    def closeEvent(self, x):
        self.reactor.stop()  
    
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = readout_histgram(reactor)
    widget.show()
    reactor.run()