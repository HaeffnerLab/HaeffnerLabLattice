from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from twisted.internet.defer import inlineCallbacks


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
        self.connect_labrad()
    
    def create_layout(self):
        layout = QtGui.QGridLayout()
        plot_layout = self.create_plot_layout()
        layout.addLayout(plot_layout, 0, 0, 1, 4)
        thresholdLabel = QtGui.QLabel("Threshold (Photon Counts Per Readout)")
        binsLabel = QtGui.QLabel("Bins")
        for l in [thresholdLabel, binsLabel]:
            l.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.threshold = QtGui.QSpinBox()
        self.threshold.setKeyboardTracking(False)
        self.threshold.setValue(self.thresholdVal)
        self.bins = QtGui.QSpinBox()
        self.bins.setKeyboardTracking(False)
        self.bins.setRange(1, 200)
        self.bins.setValue(50)
        layout.addWidget(thresholdLabel, 1, 0)
        layout.addWidget(self.threshold, 1, 1)
        layout.addWidget(binsLabel, 1, 2)
        layout.addWidget(self.bins, 1, 3)
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
        self.bins.valueChanged.connect(self.on_new_bins)
    
    def on_new_bins(self, bins):
        if self.last_data is not None:
            self.updade_histogram(self.last_data, bins)
    
    def on_key_press(self, event):
        if event.button == 2:
            xval = int(round(event.xdata))
            self.threshold.setValue(xval)
    
    def on_new_data(self, readout):
        self.last_data = readout
        bins = self.bins.value()
        self.updade_histogram(readout, bins)
    
    def updade_histogram(self, data, bins):
        #remove old histogram
        if self.last_hist is not None: 
            for obj in self.last_hist: obj.remove()
        self.last_hist = self.axes.hist(data, bins = bins, color = 'blue', normed = 'True')[2]    
        self.canvas.draw()
      
    def thresholdChange(self, threshold):
        self.thresholdLine.remove()
        self.thresholdLine = self.axes.axvline(threshold, ymin=0, ymax= 200, linewidth=3.0, color = 'r', label = 'Threshold')
        self.canvas.draw()
    
    @inlineCallbacks
    def connect_labrad(self):
        from connection import connection
        self.cxn = connection()
        yield self.cxn.connect()
        yield self.cxn.dv.signal__new_parameter_dataset(99999)
        yield self.cxn.dv.addListener(listener = self.on_new_dataset, source = None, ID = 99999)
    
    @inlineCallbacks
    def on_new_dataset(self, x, y):
        if y[3] == 'Histogram729':
            dataset = y[0]
            datasetName = y[1]
            directory = y[2]
            yield self.cxn.dv.cd(directory)
            yield self.cxn.dv.open(dataset)
            data = yield self.cxn.dv.get()
            print data
            print dataset, datasetName, directory
                                          
    def closeEvent(self, x):
        self.reactor.stop()  
    
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = readout_histgram(reactor, threshold = 20, init_data = [0,1,2,3,50,51,52]*5)
    widget.show()
    reactor.run()