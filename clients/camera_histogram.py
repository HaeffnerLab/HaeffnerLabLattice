from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
import numpy

class config_729_hist(object):
    #IDs for signaling
    ID_A = 99998
    #data vault comment
    dv_parameter = 'HistogramCameraConfidence'

c = config_729_hist

class camera_histogram(QtGui.QWidget):
    def __init__(self, reactor, cxn = None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.reactor = reactor
        self.cxn = cxn
        self.last_data = None
        self.last_hist = None
        self.subscribed = [False,False]
        self.create_layout()
        self.connect_labrad()
    
    def create_layout(self):
        layout = QtGui.QVBoxLayout()
        plot_layout = self.create_plot_layout()
        layout.addLayout(plot_layout)
        self.setLayout(layout)
   
    def create_plot_layout(self):
        layout = QtGui.QVBoxLayout()
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_xlim(left = 0, right = 1)
        self.axes.set_ylim(bottom = 0, top = 50)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        self.axes.set_title('Camera Readout', fontsize = 22)
        self.fig.tight_layout()
        layout.addWidget(self.mpl_toolbar)
        layout.addWidget(self.canvas)
        return layout
    
    def on_new_data(self, readout):
        self.last_data = readout
        self.updade_histogram(readout)
    
    def updade_histogram(self, data):
        #remove old histogram
        if self.last_hist is not None:
            self.last_hist.remove()
            #explicitly delete the refrence although not necessary
            del self.last_hist
        self.last_hist = self.axes.bar(data[:,0], data[:,1], width = numpy.max(data[:,0])/len(data[:,0]))
        #redo the limits
        x_maximum = data[:,0].max()
        self.axes.set_xlim(left = 0)
        if x_maximum > self.axes.get_xlim()[1]:
            self.axes.set_xlim(right = x_maximum)
        self.axes.set_ylim(bottom = 0)
        y_maximum = data[:,1].max()
        if y_maximum > self.axes.get_ylim()[1]:
            self.axes.set_ylim(top = y_maximum)
        self.canvas.draw()
    
    @inlineCallbacks
    def connect_labrad(self):
        if self.cxn is None:
            from common.clients import connection
            self.cxn = connection.connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            yield self.subscribe_data_vault()
        except Exception,e:
            print e
            self.setDisabled(True)
        yield self.cxn.add_on_connect('Data Vault', self.reinitialize_data_vault)
        yield self.cxn.add_on_disconnect('Data Vault', self.disable)
        
    @inlineCallbacks
    def subscribe_data_vault(self):
        server = yield self.cxn.get_server('Data Vault')
        yield server.signal__new_parameter_dataset(c.ID_A, context = self.context)
        yield server.addListener(listener = self.on_new_dataset, source = None, ID = c.ID_A, context = self.context)
        self.subscribed[0] = True

    @inlineCallbacks
    def reinitialize_data_vault(self):
        self.setDisabled(False)
        server = yield self.cxn.get_server('Data Vault')
        yield server.signal__new_parameter_dataset(c.ID_A, context = self.context)
        if not self.subscribed[0]:
            yield server.addListener(listener = self.on_new_dataset, source = None, ID = c.ID_A, context = self.context)
            self.subscribed[0] = True

    @inlineCallbacks
    def disable(self):
        self.setDisabled(True)
        yield None
            
    @inlineCallbacks
    def on_new_dataset(self, x, y):
        if y[3] == c.dv_parameter:
            dv = yield self.cxn.get_server('Data Vault')
            dataset = y[0]
            directory = y[2]
            yield dv.cd(directory, context = self.context)
            yield dv.open(dataset, context = self.context)
            data = yield dv.get( context = self.context)
            data = data.asarray
            yield deferToThread(self.on_new_data, data)
            yield dv.cd([''], context = self.context)
                                          
    def closeEvent(self, x):
        self.reactor.stop()  
    
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = camera_histogram(reactor)
    widget.show()
    reactor.run()