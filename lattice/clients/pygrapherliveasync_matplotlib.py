"""
Version 2.6

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
import numpy as np
import time
from grapherwindow import ApplicationWindow

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
    
    def waitfor(self):
        #set up a timer
        #start looping call
            #check if timer expired - then return False
            try:
                data_vault.get('plot')
            except:
                pass
            #if this paramter exists return True
      
#    # returns the number of things to plot
#    @inlineCallbacks
#    def getPlotnum(self,context):
#        variables = yield self.cxn.data_vault.variables(context = context)
#        plotNum = len(variables[1])
#        returnValue(plotNum) 

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
        print 'in empty, waiting to acquire'
        yield self.accessingData.acquire()
        del(self.data)
        self.data = None
        print 'self data should be none now'
        self.accessingData.release()
      


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
        answer = yield datasatObjcet.waitforparameter()
        if answer:
            pass
        else:
            #datasetObject.close()
            #del(datasetObject)
        #subscribe to signal
        #create a new one shot timer
        
        
        #if windows request the overlay, update those. else, create a new window.
        overlayWindows = self.getOverlayingWindows()
        if overlayWindows:
            self.dwDict[datasetObject] = overlayWindows
            for window in overlayWindows:
                window.qmc.initializeDataset(dataset)
        else:
            win = self.newGraph(dataset, context)
            #yield win.doneMaking
            self.dwDict[datasetObject] = [win]
            win.qmc.initializeDataset(dataset)
            #del(indep)
            #win.qmc.setPlotParameters()
            #win.qmc.refreshPlots()
            
    def startTimer(self): 
        lc = LoopingCall(self.timerEvent)
        lc.start(GraphRefreshTime)
        
    @inlineCallbacks
    def timerEvent(self):
#        newDataWindows = set()
        for datasetObject in self.dwDict.keys():
        # stuff you want timed goes here
            if (datasetObject.data != None):
                #print self.datasetObject.data
                windowsToDrawOn = self.dwDict[datasetObject]
                data = datasetObject.data
                yield datasetObject.emptyDataBuffer()
                for i in windowsToDrawOn:
                    i.qmc.setPlotData(datasetObject.dataset, data)
        
        
##                    newDataWindows.add((i,datasetObject.dataset))
#        for window,dataset in newDataWindows:
#            window.qmc.drawPlot(dataset)
#        windowlist = set()
#        for l in self.dwDict.values():
#            for window in l:
#                windowlist.add(window)
#        noDataWindows = windowlist.difference(newDataWindows)
#        for window in noDataWindows:
#            window.qmc.refreshPlot()

    
    # create a new graph, also sets up a Window ID so that if a graph...
    # ... asks for plot Overlay, it can be id
    def newGraph(self, dataset, context):
        win = ApplicationWindow(self.cxn, context, dataset)
        win.show()
        #time.sleep(2)
        return win
    
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