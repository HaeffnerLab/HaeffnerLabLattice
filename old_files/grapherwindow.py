from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import numpy as np

class sampleWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
    
#    def resizeEvent(self, event):
#        print 'resized widget'

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
        # checkbox to change boundaries
        self.cb2 = QtGui.QCheckBox('Overlay', self)
        self.cb2.move(500, 35)
        self.cb2.stateChanged.connect(self.overlayDataSignal)
        # button to fit data on screen
        fitButton = QtGui.QPushButton("Fit", self)
        fitButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        fitButton.move(390, 32)
        fitButton.clicked.connect(self.fitDataSignal)
        print 'done init'
    
    # Overlay Data
    def overlayDataSignal(self, state):
        if state == QtCore.Qt.Checked:
            self.overlayCheckBoxState = 1                
        else: # box is not checked
            self.overlayCheckBoxState = 0
    
    def checkIfOtherWindowsWantOverlay(self):
        self.overlaidWindows = []
        for i in Connections.dwDict.keys():
            values = Connections.dwDict[i]
            for j in values:
                if Connections.j.cb2.isChecked():
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
        #self.qmc.killTimer(self.qmc.timer)
        if (self.overlayCheckBoxState == 1):
            # "uncheck" the overlay checkbox
            self.cb2.toggle()
            # Then don't do anything else since this window closes anyway
        else:
            pass         


class Qt4MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self, parent):    
        # instantiate figure
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)      
        self.cnt = 0
        self.autoscrollFlag = 0
        self.dataDict ={}
        self.data = None 
        # create plot 
        self.ax = self.fig.add_subplot(111)
        self.ax.grid()
        self.ax.set_xlim(0, 500)# add constants
        self.ax.set_ylim(-1, 100)
        self.ax.set_autoscale_on(False) # disable figure-wide autoscale
        self.draw()
        self.old_size = self.ax.bbox.width, self.ax.bbox.height
        
        (self.xmin,self.xmax),(self.ymin,self.ymax) = self.ax.get_xlim(), self.ax.get_ylim()
        
        self.background = self.copy_from_bbox(self.ax.bbox)
        self.indep = [[], [], []] ####for now
        self.plots = [[], [], []]
        
    # Initialize a place in the dictionary for the dataset
    def initializeDataset(self, dataset):
        self.dataDict[dataset] = None
   
    def setPlotData(self, dataset, data):
        print 'setting plot data now'
        if (self.dataDict[dataset] == None):
            self.dataDict[dataset] = data
        else:
            self.dataDict[dataset] = np.append(self.dataDict[dataset], data, 0)
    
    def refreshPlot(self):
        if self.plots[0] != []:
            self.plots = self.flatten(self.plots)
            self.ax.draw_artist(self.plots[0])
            self.ax.draw_artist(self.plots[1]) 
            self.ax.draw_artist(self.plots[2])
            self.blit(self.ax.bbox)
    
    # plot the data
    def drawPlot(self, dataset):
        print 'drawing plot now'
        data = self.dataDict[dataset]     
                
        # have to redraw whole canvas if size changes
####        current_size = self.ax.bbox.width, self.ax.bbox.height
####        if self.old_size != current_size:
####            print 'size change'
####            self.old_size = current_size
####            self.ax.clear()
####            self.ax.grid()
####            self.ax.legend()
####            self.draw()
####            self.ax_background = self.copy_from_bbox(self.ax.bbox)
####            self.restore_region(self.ax_background, bbox=self.ax.bbox)
                    
        # update plot
        self.dep = data.transpose()[0]
        self.indep[0] = data.transpose()[1]
        self.indep[1] = data.transpose()[2]
        self.indep[2] = data.transpose()[3]
        
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
            self.plots = self.flatten(self.plots)
            self.plots[0].set_data(self.dep,self.indep[0])
            self.plots[1].set_data(self.dep,self.indep[1])
            self.plots[2].set_data(self.dep,self.indep[2])
            self.ax.draw_artist(self.plots[0])
            self.ax.draw_artist(self.plots[1]) 
            self.ax.draw_artist(self.plots[2])
            self.blit(self.ax.bbox)
 
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
        
    # Overlay Data
    def overlayDataSignal(self, state):
        if state == QtCore.Qt.Checked:
            self.overlayCheckBoxState = 1                
        else: # box is not checked
            self.overlayCheckBoxState = 0
    
    def checkIfOtherWindowsWantOverlay(self):
        self.overlaidWindows = []
        for i in Connections.dwDict.keys():
            values = Connections.dwDict[i]
            for j in values:
                if Connections.j.cb2.isChecked():
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
        #self.qmc.killTimer(self.qmc.timer)
        if (self.overlayCheckBoxState == 1):
            # "uncheck" the overlay checkbox
            self.cb2.toggle()
            # Then don't do anything else since this window closes anyway
        else:
            pass