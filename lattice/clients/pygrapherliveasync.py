"""
Version 2.9

Assumptions: number of axes of data doesn't change per dataset

Features:

Autoscroll checkbox
Fit button, fits all data on the screen
Opens window upon new dataset
Opens previous datasets
Overlays incoming data

"""
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock, Deferred
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
import numpy as np
import time

GraphRefreshTime = .1; # s, how often plot updates
scrollfrac = .75; # Data reaches this much of the screen before auto-scroll takes place

# NOTE!! The grapher can only see signals if the signals are created in the same directory that the grapher is in.

class Dataset(QtCore.QObject):
    
    """Class to handle incoming data and prepare them for plotting """
    def __init__(self, cxn, context, dataset, directory):
        super(Dataset, self).__init__()
        self.accessingData = DeferredLock()
        self.cxn = cxn
        self.context = context # context of the first dataset in the window
        self.dataset = dataset
        self.directory = directory
        self.data = None
        self.hasPlotParameter = 0
        self.cnt = 0
        self.setupDataListener(self.context)
        
    # open dataset in order to listen for new data signals in current context        
    @inlineCallbacks
    def openDataset(self):
        yield self.cxn.data_vault.cd(self.directory, context = self.context)
        yield self.cxn.data_vault.open(self.dataset, context = self.context)
        
    @inlineCallbacks
    def listenForPlotParameter(self):
        for i in range(600):
            parameters = yield self.cxn.data_vault.get_parameters(context = self.context)
            if (parameters != None):
                for (parameterName, value) in parameters:
                    if (str(parameterName) == 'plotLive'):
                        self.hasPlotParameter = 1
                        returnValue(self.hasPlotParameter)
            yield deferToThread(time.sleep, .1)
        returnValue(self.hasPlotParameter)
            
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
      
class sampleWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
    
#    def resizeEvent(self, event):
#        print 'resized widget'

class ApplicationWindow(QtGui.QMainWindow):
    """Creates the window for the new plot"""
    def __init__(self, cxn, context, dataset, directory, winID):
        self.cxn = cxn
        self.context = context
        self.dataset = dataset
        self.directory = directory
        self.winID = winID
        self.manuallyLoaded = True
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("Live Grapher - Dataset " + str(self.dataset))
        self.main_widget = sampleWidget() #self.main_widget = QtGui.QWidget(self)     
        # create a vertical box layout widget
        vbl = QtGui.QVBoxLayout(self.main_widget)
        # instantiate our Matplotlib canvas widget
        self.qmc = Qt4MplCanvas(self.main_widget)
        self.qmc.setParent(self.main_widget) 
        # instantiate the navigation toolbar
        ntb = NavigationToolbar(self.qmc, self.main_widget)
        vbl.addWidget(ntb)
        vbl.addWidget(self.qmc)
        # set the focus on the main widget
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        # add menu
        self.create_menu()
        # checkbox to change boundaries
        self.cb1 = QtGui.QCheckBox('Autoscroll', self)
        self.cb1.move(290, 33)
        self.cb1.stateChanged.connect(self.toggleAutoscroll)
        # checkbox to change bnooundaries
        self.cb2 = QtGui.QCheckBox('Overlay', self)
        self.cb2.move(500, 35)
        # button to fit data on screen
        fitButton = QtGui.QPushButton("Fit", self)
        fitButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        fitButton.move(390, 32)
        fitButton.clicked.connect(self.fitDataSignal) 

    # handles toggling the autoscroll feature        
    def toggleAutoscroll(self, state):
        if state == QtCore.Qt.Checked:
            self.qmc.setAutoscrollFlag(1)
        else:
            self.qmc.setAutoscrollFlag(0)
                   
    # instructs the graph to update the boundaries to fit all the data
    def fitDataSignal(self):
        if (self.cb1.isChecked()): # make sure autoscroll is off otherwise it will undo this operation
            self.cb1.toggle()
        self.qmc.fitData()
    
    # handles loading a new plot
    def load_plot(self): 
        text, ok = QtGui.QInputDialog.getText(self, 'Open Dataset', 'Enter a dataset:')        
        if ok:
            #MR some type checking that is must be an integer. This won't be necessary when we switch to the browser.
            dataset = int(text)
        text2, ok = QtGui.QInputDialog.getText(self, 'Open Dataset', 'Enter a directory:')        
        if ok:
            directory = str(text2)
            #MR some type checking that is must be an integer. This won't be necessary when we switch to the browser.
            self.parent.newDataset(dataset, directory, self.manuallyLoaded)
     
    # about menu        
    def on_about(self):
        msg = """ Live Grapher for LabRad! """
        QtGui.QMessageBox.about(self, "About the demo", msg.strip())

    # creates the menu
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_file_action = self.create_action("&Load plot",
            shortcut="Ctrl+L", slot=self.load_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Close Window", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    # menu - related
    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    # menu - related
    def create_action( self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
    
    def closeEvent(self, event):
        #self.qmc.killTimer(self.qmc.timer)
        if (self.cb2.isChecked()):
            # "uncheck" the overlay checkbox
            self.cb2.toggle()
            # Then don't do anything else since this window closes anyway
        Connections.removeWindowFromDictionary(self.winID)


class Qt4MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self, parent):    
        # instantiate figure
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)      
        self.cnt = 0
        self.dataDict = {}
        self.plotDict = {}
        self.data = None 
        self.autoscrollFlag = 0
        # create plot 
        self.ax = self.fig.add_subplot(111)
        self.ax.grid()
        #self.ax.set_xlim(1324330000.0, 1324340000.0)# add constants
        self.ax.set_xlim(0, 500)
        self.ax.set_ylim(-1, 100)
        self.ax.set_autoscale_on(False) # disable figure-wide autoscale
        self.draw()
        self.old_size = self.ax.bbox.width, self.ax.bbox.height
        
        #(self.xmin,self.xmax),(self.ymin,self.ymax) = self.ax.get_xlim(), self.ax.get_ylim()
        
        self.background = self.copy_from_bbox(self.ax.bbox)

    # toggle Autoscroll (updateBoundary)
    def setAutoscrollFlag(self, autoscrollFlag):
        self.autoscrollFlag = autoscrollFlag
         
    # Initialize a place in the dictionary for the dataset
    def initializeDataset(self, dataset, directory):
        self.dataDict[dataset, directory] = None
   
    def setPlotData(self, dataset, directory, data):
        if (self.dataDict[dataset, directory] == None):# first iteration
            self.dataDict[dataset, directory] = data
            NumberOfDependentVariables = data.shape[1] - 1
#            xmin = data.transpose()[0][0]
#            Data = data.transpose()[0].tolist()
#            Data.reverse()
#            xmax = Data[0]
#            print xmin, xmax
#            self.ax.set_xlim(xmin, xmax)
            # Assuming the first colum is x values
            
            # set up independent axis, dependent axes for data, and dependent axes for plot
            # a.k.a independent variable, dependent variables, plots
            self.plotDict[dataset, directory] = [[], [[]]*NumberOfDependentVariables, [[]]*NumberOfDependentVariables]
            for i in range(NumberOfDependentVariables):
                label = 'y: ' + str(i)
                self.plotDict[dataset, directory][2][i] = self.ax.plot(self.plotDict[dataset, directory][0],self.plotDict[dataset, directory][1][i],label = label,animated=True)
            self.ax.legend()
            self.draw()            
        else:
            self.dataDict[dataset, directory] = np.append(self.dataDict[dataset, directory], data, 0) 
    
    # plot the data
    def drawPlot(self, dataset, directory):
        data = self.dataDict[dataset, directory]
        
        # note: this will work for slow datasets, need to make sure...
        #...self.plotDict[dataset][1] is not an empty set 
        
        if (data != None):
         
            NumberOfDependentVariables = data.shape[1] - 1

            # update plot
            self.plotDict[dataset, directory][0] = data.transpose()[0]
            for i in range(NumberOfDependentVariables):
                self.plotDict[dataset, directory][1][i] = data.transpose()[i+1] # in data, the y axes start with the second column
    
            # Reassign dependent axis to smaller integers (in order to fit on screen)
            self.plotDict[dataset, directory][0] = np.arange(self.plotDict[dataset, directory][0].size)
            
            self.xmin,self.xmax = self.ax.get_xlim()
                      
            # finds the maximum dependent variable value
            self.maxX = len(self.plotDict[dataset, directory][1])
            
            self.plotDict[dataset, directory][2] = self.flatten(self.plotDict[dataset, directory][2])
            for i in range(NumberOfDependentVariables):
                self.plotDict[dataset, directory][2][i].set_data(self.plotDict[dataset, directory][0],self.plotDict[dataset, directory][1][i])
                self.ax.draw_artist(self.plotDict[dataset, directory][2][i])
            self.blit(self.ax.bbox)
            
            self.updateBoundary(dataset, directory)
 
    # if the screen has reached the scrollfraction limit, it will update the boundaries
    def updateBoundary(self, dataset, directory):
        if (self.autoscrollFlag == 1): 
            cur = self.plotDict[dataset, directory][0].size
            xmin, xmax = self.ax.get_xlim()
            xwidth = xmax - xmin
            # if current x position exceeds certain x coordinate, update the screen
            if (cur > scrollfrac * xwidth + xmin):
                xmin = cur - xwidth/4
                xmax = xmin + xwidth
                self.ax.set_xlim(xmin, xmax)
                self.draw()
        else:
            pass # since updateBoundary is called every time in drawPlot()
        
    # update boundaries to fit all the data                
    def fitData(self):
        xmin, xmax = self.ax.get_xlim()
        xmax = self.maxX
        self.ax.set_xlim(0, xmax)
        self.draw()

    # to flatten lists (for some reason not built in)
    def flatten(self,l):
            out = []
            for item in l:
                    if isinstance(item, (list, tuple)):
                            out.extend(self.flatten(item))
                    else:
                            out.append(item)
            return out

class FirstWindow(QtGui.QMainWindow):
    """Creates the opening window"""
    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self)
        self.parent = parent
        self.manuallyLoaded = True
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
        text2, ok = QtGui.QInputDialog.getText(self, 'Open Dataset', 'Enter a directory:')        
        if ok:
            directory = str(text2)
            #MR some type checking that is must be an integer. This won't be necessary when we switch to the browser.
            self.parent.newDataset(dataset, directory, self.manuallyLoaded)
  
class CONNECTIONS(QtGui.QGraphicsObject):
    def __init__(self, reactor, parent=None):
        super(CONNECTIONS, self).__init__()
        self.reactor = reactor
        self.dwDict = {} # dictionary relating Dataset and ApplicationWindow
        self.winDict = {}
        self.windowIDCounter = 0
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
        print 'Connection established: now listening dataset.'

    
    # set up dataset listener    
    @inlineCallbacks
    def setupListeners(self):               
        yield self.server.signal__new_dataset_dir(99999)#, context = context)
        yield self.server.addListener(listener = self.updateDataset, source = None, ID = 99999)#, context = context)
        #yield self.cxn.data_vault.cd(DIRECTORY)
        
    # new dataset signal
    def updateDataset(self,x,y):
        print y
        dataset = int(y[0][0:5])
        directory = str(y[1][1])
        print directory
        manuallyLoaded = False
        print dataset
        self.newDataset(dataset, directory, manuallyLoaded)
 
    # Creates a new dataset and gives it an ID for identifying later (Overlaying)
    @inlineCallbacks
    def newDataset(self, dataset, directory, manuallyLoaded):
        context = yield self.cxn.context()
        datasetObject = Dataset(self.cxn, context, dataset, directory)
        yield datasetObject.openDataset()
        
        if (manuallyLoaded == True):
            self.prepareDataset(datasetObject, dataset, directory, context)
        else:        
            hasPlotParameter = yield datasetObject.listenForPlotParameter()
            if (hasPlotParameter == 1):
                self.prepareDataset(datasetObject, dataset, directory, context)
            else:
                # This data is not for plotting
                del datasetObject

    @inlineCallbacks
    def prepareDataset(self, datasetObject, dataset, directory, context):
        #yield datasetObject.setupDataListener(context)
        #if windows request the overlay, update those. else, create a new window.
        overlayWindows = self.getOverlayingWindows()
        if overlayWindows:
            self.dwDict[datasetObject] = overlayWindows
            for window in overlayWindows:
                window.qmc.initializeDataset(dataset, directory)
        else:
            win = self.newGraph(dataset, directory, context, self.windowIDCounter)
            #yield win.doneMaking
            yield deferToThread(time.sleep, .01)
            self.dwDict[datasetObject] = [win]
            self.winDict[self.windowIDCounter] = win
            self.windowIDCounter = self.windowIDCounter + 1
            win.qmc.initializeDataset(dataset, directory) 

    # create a new graph, also sets up a Window ID so that if a graph...
    # ... asks for plot Overlay, it can be id
    def newGraph(self, dataset, directory, context, winID):
        win = ApplicationWindow(self.cxn, context, dataset, directory, winID)
        win.show()
        return win
            
    def startTimer(self): 
        lc = LoopingCall(self.timerEvent)
        lc.start(GraphRefreshTime)
        
    @inlineCallbacks
    def timerEvent(self):
        for datasetObject in self.dwDict.keys():
        # stuff you want timed goes here
            windowsToDrawOn = self.dwDict[datasetObject]
            if (datasetObject.data != None):
                #print self.datasetObject.data
                data = datasetObject.data
                yield datasetObject.emptyDataBuffer()
                for i in windowsToDrawOn:
                    i.qmc.setPlotData(datasetObject.dataset, datasetObject.directory, data)
            for i in windowsToDrawOn:
                i.qmc.drawPlot(datasetObject.dataset, datasetObject.directory)
    
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
    
    def removeWindowFromDictionary(self, winID):
        win = self.winDict[winID]
        for i in self.dwDict.keys():
            values = self.dwDict[i]
            for j in values:
                if j == win:
                    self.dwDict[i].remove(j)
                     
if __name__ == '__main__':
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    Connections = CONNECTIONS(reactor)
    reactor.run()