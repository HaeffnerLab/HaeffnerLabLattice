"""
Version 2.7

Features:

Autoscroll checkbox
Fit button, fits all data on the screen
Opens window upon new dataset
Opens previous datasets
Overlays incoming data

"""
from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock, Deferred
from twisted.internet.task import LoopingCall
#from twisted.internet.threads import deferToThread
# Guidatastuff
from guidata.qt.QtGui import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMainWindow)
from guidata.qt.QtCore import SIGNAL

#---Import plot widget base class
from guiqwt.curve import CurvePlot
from guiqwt.plot import PlotManager
from guiqwt.builder import make
from guidata.configtools import get_icon
#---

from guidata.qt.QtGui import QApplication
import scipy.signal as sps, scipy.ndimage as spi
import numpy as np
import time

GraphRefreshTime = .1; # s, how often plot updates
scrollfrac = .75; # Data reaches this much of the screen before auto-scroll takes place
DIRECTORY = 'PMT Counts' # Current working directory

# NOTE!! The grapher can only see signals if the signals are created in the same directory that the grapher is in.

class Dataset(QtCore.QObject):
    
    """Class to handle incoming data and prepare them for plotting """
    def __init__(self, cxn, context, dataset):
        super(Dataset, self).__init__()
        self.accessingData = DeferredLock()
        self.cxn = cxn
        self.context = context # context of the first dataset in the window
        self.dataset = dataset
        self.data = None
        self.setupDataListener(self.context)
        
    # open dataset in order to listen for new data signals in current context        
    @inlineCallbacks
    def openDataset(self):
        yield self.cxn.data_vault.cd(DIRECTORY, context = self.context)
        yield self.cxn.data_vault.open(self.dataset, context = self.context)
        
    # sets up the listener for new data
    @inlineCallbacks
    def setupDataListener(self, context):
        yield self.cxn.data_vault.signal__data_available(11111, context = context)
        yield self.cxn.data_vault.addListener(listener = self.updateData, source = None, ID = 11111, context = context)
        #self.setupDeferred.callback(True)
         
    # new data signal
    def updateData(self,x,y):
        self.getData(self.context)
      
    # returns the current data
    @inlineCallbacks
    def getData(self,context):
        Data = yield self.cxn.data_vault.get(100, context = context)
        if (self.data == None):
            self.data = Data.asarray
        else:
            yield self.accessingData.acquire()         
            self.data = np.append(self.data, Data.asarray, 0)
            self.accessingData.release()
        
    @inlineCallbacks
    def emptyDataBuffer(self):
        yield self.accessingData.acquire()
        del(self.data)
        self.data = None
        self.accessingData.release()
      
class CanvasWidget(QWidget):
    """
    Filter testing widget
    parent: parent widget (QWidget)
    x, y: NumPy arrays
    func: function object (the signal filter to be tested)
    """
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.dataDict = {}
        self.itemDataDict = {}
        self.data = None 
        self.setMinimumSize(320, 200)
        #---guiqwt related attributes:
        self.plot = None
        self.curve_item = None
        #---
    
        # Initialize a place in the dictionary for the dataset
    def initializeDataset(self, dataset):
        self.dataDict[dataset] = None
        self.initializeCurveItems(dataset)
   
    def setPlotData(self, dataset, data):
        if (self.dataDict[dataset] == None):
            self.dataDict[dataset] = data
        else:
            self.dataDict[dataset] = np.append(self.dataDict[dataset], data, 0)
        
    def setup_widget(self, title):
        #---Create the plot widget:
        self.plot = CurvePlot(self)
        self.plot.set_antialiasing(True)
        xaxis, yaxis = self.plot.get_active_axes()
        #return [(dx, xaxis), (dy, yaxis)]
        self.plot.set_axis_limits(2, 0, 500)
        #print xaxis
        
        #---
        
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.plot)
        self.setLayout(vlayout)    
        
    def initializeCurveItems(self, dataset):
        self.itemDataDict[dataset] = [make.curve([], [], color='b'), make.curve([], [], color='g'), make.curve([], [], color='r')]
#        self.curve_item1 = make.curve([], [], color='b')
#        self.curve_item2 = make.curve([], [], color='g')
#        self.curve_item3 = make.curve([], [], color='r')
        
        items = self.itemDataDict[dataset]
        
        for i in items:
            self.plot.add_item(i)      

#        self.plot.add_item(self.curve_item1)
#        self.plot.add_item(self.curve_item2)
#        self.plot.add_item(self.curve_item3)



    def update_curve(self, dataset):
        
        data = self.dataDict[dataset]
        
        x = data.transpose()[0]
        indep = np.arange(x.size)
        y1 = data.transpose()[1]
        y2 = data.transpose()[2]
        y3 = data.transpose()[3]
        #---Update curve
#        self.curve_item1.set_data(dep, y1)
#        self.curve_item2.set_data(dep, y2)
#        self.curve_item3.set_data(dep, y3)
        
        self.itemDataDict[dataset]
        
        # could make a for loop here, but need a list for the indep variables
        # this'll do for now
        self.itemDataDict[dataset][0].set_data(indep, y1)
        self.itemDataDict[dataset][1].set_data(indep, y2)
        self.itemDataDict[dataset][2].set_data(indep, y3)
        
        cur = indep.size
        xmin, xmax = self.plot.get_axis_limits(2)
        xwidth = xmax - xmin
        # if current x position exceeds certain x coordinate, update the screen
        if (cur > scrollfrac * xwidth + xmin):
            xmin = cur - xwidth/4
            xmax = xmin + xwidth
            self.plot.set_axis_limits(2, xmin, xmax)
    
        # Update plot
        self.plot.replot()
        #---
    
    
class ApplicationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Signal filtering 2 (guiqwt)")
        self.setWindowIcon(get_icon('guiqwt.png'))
        
        hlayout = QHBoxLayout()
        central_widget = QWidget(self)
        central_widget.setLayout(hlayout)
        self.setCentralWidget(central_widget)
        #---guiqwt plot manager
        self.manager = PlotManager(self)
        #---
        
        self.qmc = CanvasWidget(self)
        self.qmc.setup_widget("Dataset")
        self.centralWidget().layout().addWidget(self.qmc)
        #---Register plot to manager
        self.manager.add_plot(self.qmc.plot)
        #---
        # checkbox to change boundaries
        self.cb2 = QtGui.QCheckBox('Overlay', self)
        self.cb2.move(350, 25)      
 
        #---Add toolbar and register manager tools
        toolbar = self.addToolBar("tools")
        self.manager.add_toolbar(toolbar, id(toolbar))
        self.manager.register_all_curve_tools()
        
    def closeEvent(self, event):
        if (self.cb2.isChecked()):
            # "uncheck" the overlay checkbox
            self.cb2.toggle()
            # Then don't do anything else since this window closes anyway
        else:
            pass  

class FirstWindow(QtGui.QMainWindow):
    """Creates the opening window"""
    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self)
        self.parent = parent
        self.setWindowTitle("Live Grapher!")
        openButton = QtGui.QPushButton("Open Dataset", self)
        #MR eventually change this to use a layout, or make this button go in a toolbar. 
        openButton.setGeometry(QtCore.QRect(0, 0, 120, 30))
        openButton.move(41, 30)
        openButton.clicked.connect(self.load_plot)
    
    # asks for a dataset to open if one wasn't opened already    
    def load_plot(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Open Dataset', 'Enter a dataset:')        
        if ok:
            #MR some type checking that is must be an integer. This won't be necessary when we switch to the browser.
            dataset = int(text)
            self.parent.newDataset(dataset)
  
class CONNECTIONS(QtGui.QGraphicsObject):
    def __init__(self, reactor, parent=None):
        super(CONNECTIONS, self).__init__()
        self.reactor = reactor
        self.dwDict = {} # dictionary relating Dataset and ApplicationWindow
        self.connect()
        self.startTimer()
        self.introWindow = FirstWindow(self)
        self.introWindow.show()

    # connect to the data vault    
    @inlineCallbacks    
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.server = yield self.cxn.data_vault
        yield self.setupListeners()
    
    # set up dataset listener    
    @inlineCallbacks
    def setupListeners(self):               
        yield self.server.signal__new_dataset(99999)#, context = context)
        yield self.server.addListener(listener = self.updateDataset, source = None, ID = 99999)#, context = context)
        yield self.cxn.data_vault.cd(DIRECTORY)
        print 'Connection established: now listening dataset.'
        
    # new dataset signal
    def updateDataset(self,x,y):
        dataset = int(y[1:5])
        self.newDataset(dataset)
 
    # Creates a new dataset and gives it an ID for identifying later (Overlaying)
    @inlineCallbacks
    def newDataset(self, dataset):
        context = yield self.cxn.context()
        datasetObject = Dataset(self.cxn, context, dataset)
        yield datasetObject.openDataset()
        #if windows request the overlay, update those. else, create a new window.
        overlayWindows = self.getOverlayingWindows()
        if overlayWindows:
            self.dwDict[datasetObject] = overlayWindows
            for window in overlayWindows:
                window.qmc.initializeDataset(dataset)
        else:
            win = self.newGraph()
            #yield win.doneMaking
            self.dwDict[datasetObject] = [win]
            win.qmc.initializeDataset(dataset)
            #del(indep)
            #win.qmc.setPlotParameters()
            #win.qmc.refreshPlots()

    # create a new graph, also sets up a Window ID so that if a graph...
    # ... asks for plot Overlay, it can be id
    def newGraph(self):
        win = ApplicationWindow()
        win.show()
        #time.sleep(2)
        return win

            
    def startTimer(self): 
        lc = LoopingCall(self.timerEvent)
        lc.start(GraphRefreshTime)
        
    @inlineCallbacks
    def timerEvent(self):
        updatedWindows = set()
        for datasetObject in self.dwDict.keys():
        # stuff you want timed goes here
            if (datasetObject.data != None):
                windowsToDrawOn = self.dwDict[datasetObject]
                data = datasetObject.data
                yield datasetObject.emptyDataBuffer()
                for i in windowsToDrawOn:
                    i.qmc.setPlotData(datasetObject.dataset, data)
                    updatedWindows.add((i,datasetObject.dataset))
        for window,dataset in updatedWindows:
            window.qmc.update_curve(dataset)


    
    # Cycles through the values in each key for checked Overlay boxes, returns the windows...
    # ...with the overlay button checked
    def getOverlayingWindows(self):
        self.overlaidWindows = []
        for i in self.dwDict.keys():
            values = self.dwDict[i]
            for j in values:
                if j.cb2.isChecked():
                    # skip duplicates
                    if j in self.overlaidWindows:
                        pass
                    else:
                        self.overlaidWindows.append(j)
        return self.overlaidWindows
                     
if __name__ == '__main__':
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    Connections = CONNECTIONS(reactor)
    reactor.run()