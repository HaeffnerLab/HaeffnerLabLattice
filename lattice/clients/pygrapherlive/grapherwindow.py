'''
The plot and all relevant plot options are managed by the Grapher Window.
'''

from PyQt4 import QtGui, QtCore
from canvas import Qt4MplCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from datavault import DataVaultWidget
import time

class GrapherWindow(QtGui.QWidget):
    """Creates the window for the new plot"""
    def __init__(self, parent, context, windowName):
#    def __init__(self, parent, context):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.context = context
        self.windowName = windowName
        self.parameterWindows = {}
        self.datasetCheckboxes = {}
        self.datasetCheckboxCounter = 0
        self.manuallyLoaded = True
        self.setWindowTitle(self.windowName)
   
        # create a vertical box layout widget
        grapherLayout = QtGui.QVBoxLayout()
        # instantiate our Matplotlib canvas widget
        self.qmc = Qt4MplCanvas(self)
        # instantiate the navigation toolbar
        ntb = NavigationToolbar(self.qmc, self)

        # Layout that involves the canvas, toolbar, graph options...etc.
        grapherLayout.addWidget(ntb)
        grapherLayout.addWidget(self.qmc)

        # Main horizontal layout
        mainLayout = QtGui.QHBoxLayout()
        # Layout that controls datasets
        datasetLayout = QtGui.QVBoxLayout() 

        mainLayout.addLayout(datasetLayout)
        mainLayout.addLayout(grapherLayout)
        
        # Layout for keeping track of datasets on a graph
        self.datasetCheckboxListWidget = QtGui.QListWidget()
        self.datasetCheckboxListWidget.setMaximumWidth(180)
        datasetLayout.addWidget(self.datasetCheckboxListWidget)

        self.setLayout(mainLayout)

        # checkbox to change boundaries
        self.cb1 = QtGui.QCheckBox('AutoScroll', self)
        #self.cb1.move(290, 23)
        self.cb1.clicked.connect(self.autoscrollSignal) 
        # checkbox to overlay new dataset
        self.cb2 = QtGui.QCheckBox('Overlay', self)
        #self.cb2.move(500, 35)
        # checkbox to toggle AutoFit
        self.cb3 = QtGui.QCheckBox('AutoFit', self)
        #self.cb3.move(290, 39)
        self.cb3.toggle()
        self.cb3.clicked.connect(self.autofitSignal) 
        # button to fit data on screen
        fitButton = QtGui.QPushButton("Fit", self)
        fitButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        fitButton.clicked.connect(self.fitDataSignal)
        
        windowNameButton = QtGui.QPushButton("Change Window Name", self)
        windowNameButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        windowNameButton.clicked.connect(self.changeWindowName)
        
        # Layout that controls graph options
        buttonBox = QtGui.QHBoxLayout()
        buttonBox.addWidget(self.cb1) 
        buttonBox.addWidget(self.cb3)
        buttonBox.addWidget(self.cb2)  
        buttonBox.addWidget(fitButton)
        buttonBox.addWidget(windowNameButton) 
        
        grapherLayout.addLayout(buttonBox)

    # adds a checkbox when a new dataset is overlaid on the graph
    def createDatasetCheckbox(self, dataset, directory):
        datasetCheckbox = QtGui.QCheckBox(str(dataset) + ' ' + str(directory[-1]), self)
        datasetCheckbox.toggle()
        datasetCheckbox.clicked.connect(self.datasetCheckboxSignal)
        self.datasetCheckboxes[dataset, directory] = datasetCheckbox
        self.datasetCheckboxListWidget.addItem('')
        self.datasetCheckboxListWidget.setItemWidget(self.datasetCheckboxListWidget.item(self.datasetCheckboxCounter), datasetCheckbox)
        self.datasetCheckboxCounter = self.datasetCheckboxCounter + 1

    def datasetCheckboxSignal(self):
        self.qmc.drawLegend()
        self.qmc.draw()

    # when the autoFit button is checked, it will uncheck the autoscroll button
    def autofitSignal(self):
        if (self.cb1.isChecked()):
            self.cb1.toggle()
    
    # when the autoscroll button is checked, it will uncheck the autoFit button        
    def autoscrollSignal(self):
        if (self.cb3.isChecked()):
            self.cb3.toggle()

    # instructs the graph to update the boundaries to fit all the data
    def fitDataSignal(self):
        if (self.cb1.isChecked()): # makes sure autoscroll is off otherwise it will undo this operation
            self.cb1.toggle()
        elif (self.cb3.isChecked()): # makes sure autoFit is off otherwise it will undo this operation
            self.cb3.toggle()
        self.qmc.fitData()
    
    def changeWindowName(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Change Window Name', 'Enter a name:')        
        if ok:
            text = str(text)
            self.parent.changeWindowName(self.windowName, text)
            self.setWindowTitle(text)
            self.windowName = text
    
    def newParameterWindow(self, dataset, directory):
        win = ParameterWindow(self, dataset, directory)
        win.show()
        self.parameterWindows[dataset, directory] = win

    def getParameters(self, dataset, directory):
        parameters = self.parent.getParameters(dataset, directory)
        return parameters                   
     
    def fileQuit(self):
        self.close()
        
    def closeEvent(self, event):
        self.qmc.endTimer()
        if (self.cb2.isChecked()):
            # "uncheck" the overlay checkbox
            self.cb2.toggle()
        # Remove this window from the dictionary so that no datasets...
        # ... are drawn to this window
        self.parent.removeWindowFromDictionary(self)
        self.parent.removeWindowFromWinDict(self.windowName)
#        self.parent.removeWindowFromWinList(self)
        self.parent.cleanUp()
        self.fileQuit()


class FirstWindow(QtGui.QWidget):
    """Creates the opening window"""
    def __init__(self, parent, context, reactor):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.context = context
        self.reactor = reactor
        self.parameterWindows = {}
        self.manuallyLoaded = True
        self.setWindowTitle("Live Grapher!")
        hbl = QtGui.QHBoxLayout()
        self.setLayout(hbl)
        self.datavaultwidget = DataVaultWidget(self, context)
        self.datavaultwidget.populateList()
        #self.datavaultwidget.show()
        hbl.addWidget(self.datavaultwidget)
        
    def newParameterWindow(self, dataset, directory):
        win = ParameterWindow(self, dataset, directory)
        win.show()
        self.parameterWindows[dataset, directory] = win

    def getParameters(self, dataset, directory):
        parameters = self.parent.getParameters(dataset, directory)
        return parameters
    
    def closeEvent(self, event):
        self.reactor.stop()                   


class ParameterWindow(QtGui.QWidget):
    """Creates the dataset-specific parameter window"""

    def __init__(self, parent, dataset, directory):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.dataset = dataset
        self.directory = directory
        self.setWindowTitle(str(dataset) + " " + str(directory))
        mainLayout = QtGui.QVBoxLayout() 
        self.parameterListWidget = QtGui.QListWidget()
        mainLayout.addWidget(self.parameterListWidget)
        self.populateList()
        self.startTimer(30000)
        self.setLayout(mainLayout)

    
    def timerEvent(self, evt):
        self.populateList()
        tstartupdate = time.clock()
    
    def populateList(self):
        self.parameters = self.parent.getParameters(self.dataset, self.directory)
        self.parameterListWidget.clear()
        if (self.parameters):
            for i in self.parameters:
                self.parameterListWidget.addItem(str(i))
