from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
import numpy

class readout_histgram(QtGui.QWidget):
    def __init__(self, reactor, cxn = None, parent=None, threshold = 1, init_data = None):
        QtGui.QWidget.__init__(self, parent)
        self.reactor = reactor
        self.cxn = cxn
        self.thresholdVal = threshold
        self.create_layout()
        self.connect_layout()
        self.last_data = None
        self.last_hist = None
        if init_data is not None:
            self.on_new_data(init_data)
        self.subscribed = False
        self.connect_labrad()
    
    def create_layout(self):
        layout = QtGui.QGridLayout()
        plot_layout = self.create_plot_layout()
        layout.addLayout(plot_layout, 0, 0, 1, 4)
        thresholdLabel = QtGui.QLabel("Threshold (Photon Counts Per Readout)")
        for l in [thresholdLabel]:
            l.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.threshold = QtGui.QSpinBox()
        self.threshold.setKeyboardTracking(False)
        self.threshold.setValue(self.thresholdVal)
        layout.addWidget(thresholdLabel, 1, 0)
        layout.addWidget(self.threshold, 1, 1)
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
      
    def thresholdChange(self, threshold):
        self.thresholdLine.remove()
        self.thresholdLine = self.axes.axvline(threshold, ymin=0, ymax= 200, linewidth=3.0, color = 'r', label = 'Threshold')
        self.canvas.draw()
    
    @inlineCallbacks
    def connect_labrad(self):
        if self.cxn is None:
            from connection import connection
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            yield self.subscribe()
            self.subscribed = True
        except Exception, e:
            print e
            print 'Not Initially Connected'
            self.setDisabled(True)
        self.cxn.on_connect['Data Vault'].append( self.reinitialize)
        self.cxn.on_disconnect['Data Vault'].append( self.disable)
        
    @inlineCallbacks
    def subscribe(self):
        yield self.cxn.servers['Data Vault'].signal__new_parameter_dataset(99999, context = self.context)
        yield self.cxn.servers['Data Vault'].addListener(listener = self.on_new_dataset, source = None, ID = 99999, context = self.context)
    
    @inlineCallbacks
    def reinitialize(self):
        self.setDisabled(False)
        yield self.cxn.servers['Data Vault'].signal__new_parameter_dataset(99999, context = self.context)
        if not self.subscribed:
            yield self.cxn.servers['Data Vault'].addListener(listener = self.on_new_dataset, source = None, ID = 99999, context = self.context)
    
    @inlineCallbacks
    def disable(self):
        self.setDisabled(True)
        yield None
        
    @inlineCallbacks
    def on_new_dataset(self, x, y):
        if y[3] == 'Histogram729':
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
    init_data = numpy.array([[0,0],[1,2],[3,50],[51,52]])
    widget = readout_histgram(reactor, threshold = 20, init_data = init_data)
    widget.show()
    reactor.run()