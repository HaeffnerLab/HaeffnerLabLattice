"""
Version 2.0

Features:

Autoscroll checkbox
Fit button, fits all data on the screen
Opens window upon new dataset
Opens previous datasets
Overlays incoming data (one window at a time)

"""

import sys
from PyQt4 import QtGui, QtCore
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from twisted.internet.defer import inlineCallbacks, returnValue

import numpy as np
from PyQt4.Qt import *
import time

GraphRefreshTime = 100; # ms, how often plot updates
scrollfrac = .75; # Data reaches this much of the screen before auto-scroll takes place
DIRECTORY = 'PMT Counts' # Current working directory
MAXDATASETS = 50 # Maximum datasets the grapher will handle
MAXDATASETSOVERLAY = 10 # Maximum number of datasets the grapher can overlay on one graph

# NOTE!! The grapher can only see signals if the signals are created in the same directory that the grapher is in.

class Dataset():
    """Class to handle incoming data and prepare them for plotting """
    def __init__(self, cxn, context, dataset):
        self.cxn = cxn
        self.context = context # context of the first dataset in the window
        self.dataset = dataset
        self.cnt = 0
        self.openDataset(self.dataset, self.context)
        self.setupDataListener(self.context)

    # open dataset in order to listen for new data signals in current context        
    @inlineCallbacks
    def openDataset(self, dataset, context):
        yield self.cxn.data_vault.cd(DIRECTORY, context = context)
        yield self.cxn.data_vault.open(dataset, context = context)
        print str(dataset) + ' is open'
        
    # sets up the listener for new data
    @inlineCallbacks
    def setupDataListener(self, context):
        yield self.cxn.data_vault.signal__data_available(11111, context = context)
        yield self.cxn.data_vault.addListener(listener = self.updateData, source = None, ID = 11111, context = context)
        print 'now listening data'

    # new data signal
    def updateData(self,x,y):
        x = str(x)
        q = x[29]
        r = x[33]
        context = [int(q), int(r)]
        context = tuple(context)
        self.getPlotData(context)   

    # Draws the plot with the available data
    @inlineCallbacks
    def getPlotData(self,context):
        if (self.cnt == 0): # initial plot setup
            self.data = yield self.getData(context) # current data
            self.plotnum = yield self.getPlotnum(self.context) # number of things to plot
            self.plots = [[]]*self.plotnum
            self.indep = [[]]*self.plotnum
            self.newPlotDataExists = True
            
        else: # take new data, append it to existing data
            newdatal = yield self.getData(context) 
            newdata = np.array(newdatal)
            self.data = np.append(self.data, newdata, 0)

    # returns the number of things to plot
    @inlineCallbacks
    def getPlotnum(self,context):
        variables = yield self.cxn.data_vault.variables(context = context)
        plotNum = len(variables[1])
        returnValue(plotNum) 
    
    # returns the current data
    @inlineCallbacks
    def getData(self,context):
        # the first data point is skipped, this ensures that the first data point is retrieved
        if (self.cnt == 0): 
            Data = yield self.cxn.data_vault.get(500, True, context = context)
        else:
            Data = yield self.cxn.data_vault.get(context = context)
        data = Data.asarray
        returnValue(data)

        
class Qt4MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self, parent, dataset):    
        
        self.dataset = dataset
        self.cnt = 0
        self.autoscrollFlag = 0
        
        # datasets overlaid on the same graph
        self.datasetsToPlot = [None]*MAXDATASETSOVERLAY # max datasets to overlay (for now)
        self.datasetsToPlot[0] = self.findDataset(self.dataset)
        self.datasetCounter = 1
        
        # instantiate figure
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        
        # create plot 
        self.ax = self.fig.add_subplot(111)
        self.ax.grid()
        self.ax.set_xlim(0, 75)# add constants
        self.ax.set_ylim(-1, 100)
        self.ax.set_autoscale_on(False) # disable figure-wide autoscale
        self.ax.legend()
        self.draw()
        self.old_size = self.ax.bbox.width, self.ax.bbox.height
        self.ax_background = self.copy_from_bbox(self.ax.bbox)
        self.timer = self.startTimer(GraphRefreshTime)
    
    # finds which datasetObject corresponds to which dataset (used for overlaying multiple datasets)       
    def findDataset(self, dataset):
        for i in range(0, (Connections.datasetCounter + 1)):
            if (Connections.datasetID[i] == dataset):
                return i
                break
            else:
                pass

    # Creates a list of datasets to plot later
    def overlayData(self,dataset):
        print dataset
        newDatasetToPlot = self.findDataset(dataset)
        self.datasetsToPlot[self.datasetCounter] = newDatasetToPlot
        self.datasetCounter = self.datasetCounter + 1
              
    # refresh the graph
    def timerEvent(self, evt):
        for datasetToPlot in range(self.datasetCounter):
            self.drawPlot(Connections.datasetList[self.datasetsToPlot[datasetToPlot]].data, datasetToPlot)
        tstopupdate = time.clock()

    # plot the data
    def drawPlot(self, data, datasetToPlot):
        
        if (self.cnt == 0): # initial variable setup
            self.plots = Connections.datasetList[self.datasetsToPlot[datasetToPlot]].plots
            self.indep = Connections.datasetList[self.datasetsToPlot[datasetToPlot]].indep
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
        dep = data.transpose()[0]
        self.indep[0] = data.transpose()[1]
        self.indep[1] = data.transpose()[2]
        self.indep[2] = data.transpose()[3]
           
        # finds the maximum dependent variable value
        self.maxX = len(dep)
        
        if (self.cnt == 0): # initial label setup       
            self.plots[0] = self.ax.plot(dep.tolist(),self.indep[0].tolist(),label = '866 ON',animated=True)
            self.plots[1] = self.ax.plot(dep.tolist(),self.indep[1].tolist(),label = '866 OFF', animated=True)
            self.plots[2] = self.ax.plot(dep.tolist(),self.indep[2].tolist(),label = 'Differential ', animated=True)
            self.cnt = self.cnt + 1
            
        else: # add the new data
            self.plots[0].set_data(dep,self.indep[0])
            self.plots[1].set_data(dep,self.indep[1])
            self.plots[2].set_data(dep,self.indep[2])
    
        # flatten the data
        self.plots = self.flatten(self.plots)
        
        # draw
        self.ax.draw_artist(self.plots[0])
        self.ax.draw_artist(self.plots[1])
        self.ax.draw_artist(self.plots[2])
    
        # redraw the cached axes rectangle
        self.blit(self.ax.bbox)
        
        # check if the axes needs to be updated
        self.updateBoundary(data)
 
    # toggle Autoscroll (updateBoundary)
    def setAutoscrollFlag(self, autoscrollFlag):
        self.autoscrollFlag = autoscrollFlag
 
    # if the screen has reached the scrollfraction limit, it will update the boundaries
    def updateBoundary(self, data):
        if (self.autoscrollFlag == 1):
            cur = data.transpose()[0][-1]
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
    def __init__(self, cxn, context, dataset, winID):
        self.toggleFlag = 0
        self.cxn = cxn
        self.context = context
        self.dataset = dataset
        self.overlayCheckBoxState = 0
        self.winID = winID
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("Live Grapher - Dataset " + str(self.dataset))
        self.main_widget = QtGui.QWidget(self)
        # create a vertical box layout widget
        vbl = QtGui.QVBoxLayout(self.main_widget)
        # instantiate our Matplotlib canvas widget
        self.qmc = Qt4MplCanvas(self.main_widget, self.dataset)
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
        self.cb2.move(500, 40)
        self.cb2.stateChanged.connect(self.overlayDataSignal)
        # button to fit data on screen
        fitButton = QPushButton("Fit", self)
        fitButton.setGeometry(QRect(0, 0, 30, 30))
        fitButton.move(390, 32)
        fitButton.connect(fitButton, SIGNAL("clicked()"), self.fitDataSignal)
    
    # Variable in charge of identifying the state of the Overlay Checkbox
    def setOverlayCheckBoxState(self,x):
        self.overlayCheckBoxState = x
        
    # Overlay Data
    def overlayDataSignal(self, state):
        if state == QtCore.Qt.Checked:
            self.overlayCheckBoxState = 1
            # make sure all other Overlay boxes are unchecked
            for i in range(Connections.winID + 1):
                if ((Connections.winlist[i].overlayCheckBoxState == 1) and i != self.winID):
                    Connections.winlist[i].cb2.toggle()
                    Connections.winlist[i].setOverlayCheckBoxState(0)
                else:
                    pass
                
            # Tell Connections to stop making new windows for new datasets 
            Connections.setOverlayFlag(1, self.winID)
        else:
            # Tell Connections to start making new windows for new datasets
            Connections.setOverlayFlag(0, self.winID)
            
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
        QMessageBox.about(self, "About the demo", msg.strip())

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
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

class FirstWindow(QtGui.QMainWindow):
    """Creates the opening window"""
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
                
        self.setWindowTitle("Live Grapher!")
        self.main_widget = QtGui.QWidget(self)
        
        openButton = QPushButton("Open Dataset", self)
        openButton.setGeometry(QRect(0, 0, 120, 30))
        openButton.move(41, 30)
        openButton.connect(openButton, SIGNAL("clicked()"), self.load_plot)
    
    # asks for a dataset to open if one wasn't opened already    
    def load_plot(self):
    
        text, ok = QtGui.QInputDialog.getText(self, 'Open Dataset', 
        'Enter a dataset:')        
        if ok:
            dataset = int(text)
            print dataset
            Connections.newDataset(dataset)
  
class CONNECTIONS():
    def __init__(self, reactor, parent=None):
        self.reactor = reactor
        self.winlist = []
        self.datasetList = []
        self.datasetCounter = -1 # arrays start with 0
        self.datasetID = [None]*MAXDATASETS # max datasets (for now)
        self.winID = -1 # arrays start with 0
        self.overlayFlag = 0
        self.connect()
        self.introWindow = FirstWindow()
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
        print 'now listening dataset'
    
    # new dataset signal
    def updateDataset(self,x,y):
        dataset = int(y[1:5])
        print dataset
        self.newDataset(dataset)
 
    # Creates a new dataset and gives it an ID for identifying later (Overlaying)
    @inlineCallbacks
    def newDataset(self, dataset):
        self.datasetCounter = self.datasetCounter + 1
        self.datasetID[self.datasetCounter] = dataset
        context = yield self.cxn.context()
        self.datasetObject = Dataset(self.cxn, context, dataset)
        self.datasetList.append(self.datasetObject)
        self.newGraph(dataset, context)
    
    # create a new graph, also sets up a Window ID so that if a graph...
    # ... asks for plot Overlay, it can be identified
    def newGraph(self, dataset, context):
        if (self.overlayFlag == 0):
            self.winID = self.winID + 1
            self.win = ApplicationWindow(self.cxn, context, dataset, self.winID)
            self.win.show()
            self.winlist.append(self.win)
        else:
            print 'no more new windows!'
            # send the new dataset to the window asking for it
            self.winlist[self.windowAskingForOverlay].qmc.overlayData(dataset)
    
    # In charge of turning Overlay on and off
    def setOverlayFlag(self, x, winID):
        self.overlayFlag = x
        if (x == 1):
            self.windowAskingForOverlay = winID
        else:
            pass

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