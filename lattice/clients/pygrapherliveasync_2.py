"""
Version 2.5

Features:

Autoscroll checkbox
Fit button, fits all data on the screen
Opens window upon new dataset
Opens previous datasets
Overlays incoming data

"""
from PyQt4 import QtGui, QtCore
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np
import time

GraphRefreshTime = 100; # ms, how often plot updates
scrollfrac = .75; # Data reaches this much of the screen before auto-scroll takes place
DIRECTORY = 'PMT Counts' # Current working directory

# NOTE!! The grapher can only see signals if the signals are created in the same directory that the grapher is in.

class Dataset(QtCore.QObject):
    dataReady = QtCore.pyqtSignal()
    """Class to handle incoming data and prepare them for plotting """
    def __init__(self, cxn, context, dataset):
        QtCore.QObject.__init__(self)
        self.cxn = cxn
        self.context = context # context of the first dataset in the window
        self.dataset = dataset
        self.openDataset(self.dataset, self.context)
        self.plotnum = self.getPlotnum(context)
        self.setupDataListener(self.context)

    # open dataset in order to listen for new data signals in current context        
    @inlineCallbacks
    def openDataset(self, dataset, context):
        yield self.cxn.data_vault.cd(DIRECTORY, context = context)
        yield self.cxn.data_vault.open(dataset, context = context)
        
    # sets up the listener for new data
    @inlineCallbacks
    def setupDataListener(self, context):
        yield self.cxn.data_vault.signal__data_available(11111, context = context)
        yield self.cxn.data_vault.addListener(listener = self.updateData, source = None, ID = 11111, context = context)

    # new data signal
    def updateData(self,x,y):
        self.getData(self.context)   
        
    # returns the number of things to plot
    @inlineCallbacks
    def getPlotnum(self,context):
        variables = yield self.cxn.data_vault.variables(context = context)
        plotNum = len(variables[1])
        returnValue(plotNum) 
    
    # returns the current data
    @inlineCallbacks
    def getData(self,context):
        data = yield self.cxn.data_vault.get(100, context = context)
        self.dataReady.emit()
      
class Qt4MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self, parent):    
        # instantiate figure
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        self.cnt = 0
        self.autoscrollFlag = 0 
        # create plot 
        self.ax = self.fig.add_subplot(111)
        self.ax.grid()
        self.ax.set_xlim(0, 500)# add constants
        self.ax.set_ylim(-1, 100)
        self.ax.set_autoscale_on(False) # disable figure-wide autoscale
        #self.draw()
        self.old_size = self.ax.bbox.width, self.ax.bbox.height
        self.ax_background = self.copy_from_bbox(self.ax.bbox)
    
    def setPlotParameters(self, indep, plots):
        self.plots = plots
        self.indep = indep
   
    def setInitialPlotData(self, data):
        self.data = data
               
    def appendNewData(self, newdata):
        self.data = np.append(self.data, newdata, 0)
               
    # refresh the graph
    def timerEvent(self, evt):
        #print 'timer event', self
        # stuff you want timed goes here
        self.drawPlot(self.datasetID)
        tstopupdate = time.clock()
       
    # plot the data
    def drawPlot(self, datasetID):
                      
        if (self.cnt == 0): # initial variable setup
            self.datasetID = datasetID
            self.timer = self.startTimer(GraphRefreshTime)
        else:
            pass
                
        # have to redraw whole canvas if size changes
        current_size = self.ax.bbox.width, self.ax.bbox.height
        if self.old_size != current_size:
            print 'size change'
            self.old_size = current_size
            self.ax.clear()
            self.ax.grid()
            self.ax.legend()
            self.draw()
            self.ax_background = self.copy_from_bbox(self.ax.bbox)
            self.restore_region(self.ax_background, bbox=self.ax.bbox)
                    
        # update plot
        self.dep = self.data.transpose()[0]
        self.indep[0] = self.data.transpose()[1]
        self.indep[1] = self.data.transpose()[2]
        self.indep[2] = self.data.transpose()[3]
        
        # Reassign dependent axis to smaller integers (in order to fit on screen)
        self.dep = np.arange(self.dep.size)
                  
        # finds the maximum dependent variable value
        self.maxX = len(self.dep)
        
        if (self.cnt == 0): # initial label setup       
            self.plots[0] = self.ax.plot(self.dep.tolist(),self.indep[0].tolist(),label = '866 ON',animated=True)
            self.plots[1] = self.ax.plot(self.dep.tolist(),self.indep[1].tolist(),label = '866 OFF', animated=True)
            self.plots[2] = self.ax.plot(self.dep.tolist(),self.indep[2].tolist(),label = 'Differential ', animated=True)
            self.ax.legend()
            self.draw()
            self.cnt = self.cnt + 1
            
        else: # add the new data

            self.plots[0].set_data(self.dep,self.indep[0])
            self.plots[1].set_data(self.dep,self.indep[1])
            self.plots[2].set_data(self.dep,self.indep[2])
    
        # flatten the data
        self.plots = self.flatten(self.plots)
               
        # draw
        self.ax.draw_artist(self.plots[0])
        self.ax.draw_artist(self.plots[1]) 
        self.ax.draw_artist(self.plots[2])
            
        # redraw the cached axes rectangle
        self.blit(self.ax.bbox)
                
        # check if the axes needs to be updated
        self.updateBoundary(self.data)
 
    # toggle Autoscroll (updateBoundary)
    def setAutoscrollFlag(self, autoscrollFlag):
        self.autoscrollFlag = autoscrollFlag
 
    # if the screen has reached the scrollfraction limit, it will update the boundaries
    def updateBoundary(self, data):
        if (self.autoscrollFlag == 1): # or self.firstBoundaryUpdate == True):
            cur = self.dep.size
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

class ApplicationWindow(QtGui.QMainWindow):
    """Creates the window for the new plot"""
    def __init__(self, cxn, context, dataset):
        self.toggleFlag = 0
        self.cxn = cxn
        self.context = context
        self.dataset = dataset
        self.overlayCheckBoxState = 0
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("Live Grapher - Dataset " + str(self.dataset))
        self.main_widget = QtGui.QWidget(self)
        # create a vertical box layout widget
        vbl = QtGui.QVBoxLayout(self.main_widget)
        # instantiate our Matplotlib canvas widget
        self.qmc = Qt4MplCanvas(self.main_widget)
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
        # checkbox to change boundaries
        self.cb2 = QtGui.QCheckBox('Overlay', self)
        self.cb2.move(500, 35)
        self.cb2.stateChanged.connect(self.overlayDataSignal)
        # button to fit data on screen
        fitButton = QtGui.QPushButton("Fit", self)
        fitButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        fitButton.move(390, 32)
        fitButton.clicked.connect(self.fitDataSignal)
        
    # Overlay Data
    def overlayDataSignal(self, state):
        if state == QtCore.Qt.Checked:
            self.overlayCheckBoxState = 1                
            # Tell Connections to stop making new windows for new datasets 
            Connections.setOverlayFlag(1)
        else: # box is not checked
            self.overlayCheckBoxState = 0
            if (self.checkIfOtherWindowsWantOverlay() == False):
                # Tell Connections to start making new windows for new datasets
                Connections.setOverlayFlag(0)
    
    def checkIfOtherWindowsWantOverlay(self):
        self.overlaidWindows = []
        for i in Connections.dwDict.keys():
            values = Connections.dwDict[i]
            for j in values:
                if Connections.winlist[j].cb2.isChecked():
                    return True
        return False        
                   
    # instructs the graph to update the boundaries to fit all the data
    def fitDataSignal(self):
        if (self.toggleFlag == 1): # make sure autoscroll is off otherwise it will undo this operation
            self.cb1.toggle()
            self.qmc.setAutoscrollFlag(0)
            self.qmc.fitData()
        else:
            self.qmc.fitData()
    
    # handles toggling the autoscroll feature        
    def toggleAutoscroll(self, state):

        if state == QtCore.Qt.Checked:
            self.qmc.setAutoscrollFlag(1)
            self.toggleFlag = 1
        else:
            self.qmc.setAutoscrollFlag(0)
            self.toggleFlag = 0

    # handles loading a new plot
    def load_plot(self): 
        text, ok = QtGui.QInputDialog.getText(self, 'Open Dataset', 
            'Enter a dataset:')
        if ok:
            dataset = int(text)
            print dataset
            Connections.newDataset(dataset)
    
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
    def create_action(  self, text, slot=None, shortcut=None, 
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
        if (self.overlayCheckBoxState == 1):
            # "uncheck" the overlay checkbox
            self.cb2.toggle()
            self.qmc.killTimer(self.qmc.timer)
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
  
class CONNECTIONS():
    def __init__(self, reactor, parent=None):
        self.reactor = reactor
        self.dwDict = {} # dictionary relating Dataset and ApplicationWindow
        self.connect()
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
        #if windows request the overlay, update those. else, create a new window.
        overlayWindows = self.getOverlayingWindows()
        if overlayWindows:
            self.dwDict[datasetObject] = overlayWindows
        else:
            win = self.newGraph(dataset, context) 
            self.dwDict[datasetObject] = [win]
        datasetObject.dataReady.connect(self.drawThePlot(datasetObject))
    
    def drawThePlot(self, datasetObject):
        def f():
            self.doDrawThePlot(datasetObject)
        return f
    
    def doDrawThePlot(self, datasetObject): 
        print 'new data'
        print datasetObject
        windowsToDrawOn = self.dwDict[datasetObject]
        for i in windowsToDrawOn:
#            self.plots = self.datasetList[datasetID].plots
#            self.indep = self.datasetList[datasetID].indep
#            data = self.datasetList[datasetID].data
#            if self.winlist[i].qmc.cnt == 0:
#                self.winlist[i].qmc.setPlotParameters(self.plots, self.indep)
#            self.winlist[i].qmc.setInitialPlotData(data)
#            self.winlist[i].qmc.drawPlot(datasetID)
    
###    def drawNewDataOnPlot(self, datasetID):
###        windowsToDrawOn = self.dwDict[datasetID]
###        for i in windowsToDrawOn:
###            newdata = self.datasetList[datasetID].newdata
###            self.winlist[i].qmc.appendNewData(newdata)
###            self.winlist[i].qmc.drawPlot(datasetID)
    
    # create a new graph, also sets up a Window ID so that if a graph...
    # ... asks for plot Overlay, it can be id
    def newGraph(self, dataset, context):
        win = ApplicationWindow(self.cxn, context, dataset)
        win.show()
        return win
    
    # Cycles through the values in each key for checked Overlay boxes, returns the windows...
    # ...with the overlay button checked
    def getOverlayingWindows(self):
        self.overlaidWindows = []
        for i in self.dwDict.keys():
            values = self.dwDict[i]
            for j in values:
                if self.winlist[j].cb2.isChecked():
                    # skip duplicates
                    if j in self.overlaidWindows:
                        pass
                    else:
                        self.overlaidWindows.append(j)
        return self.overlaidWindows
            
    # Quade!! Stop the reactor!
    @inlineCallbacks                  
    def closeEvent(self):
        self.reactor.stop()
         
if __name__ == '__main__':
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    Connections = CONNECTIONS(reactor)
    reactor.run()