'''
The plot and all relevant plot options are managed by the Grapher Window.
'''

from PyQt4 import QtGui, QtCore
from canvas import Qt4MplCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from datavault import DataVaultWidget

class GrapherWindow(QtGui.QMainWindow):
    """Creates the window for the new plot"""
    def __init__(self, parent, cxn, context, dataset, directory):
        self.parent = parent
        self.cxn = cxn
        self.context = context
        self.dataset = dataset
        self.directory = directory
        self.manuallyLoaded = True
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("Live Grapher - Dataset " + str(self.dataset))
        self.main_widget = QtGui.QWidget(self)     
        self.setCentralWidget(self.main_widget)
        # create a vertical box layout widget
        vbl = QtGui.QVBoxLayout()
        #vbl.addStretch(1)
        # instantiate our Matplotlib canvas widget
        self.qmc = Qt4MplCanvas(self.main_widget, self)
        # instantiate the navigation toolbar
        ntb = NavigationToolbar(self.qmc, self.main_widget)

        vbl.addWidget(ntb)
        vbl.addWidget(self.qmc)

        hbl = QtGui.QHBoxLayout(self.main_widget)
        self.datavaultwidget = DataVaultWidget(self)
        self.datavaultwidget.populateList()
        #self.datavaultwidget.show()
        hbl.addWidget(self.datavaultwidget)
        hbl.addLayout(vbl)
#        
#        self.main_widget.setLayout(hbl)
        

        # set the focus on the main widget
        self.main_widget.setFocus()
        # add menu
        self.create_menu()
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
        #fitButton.move(390, 32)
        fitButton.clicked.connect(self.fitDataSignal)
        
        buttonBox = QtGui.QHBoxLayout()
        buttonBox.addWidget(self.cb1) 
        buttonBox.addWidget(self.cb2) 
        buttonBox.addWidget(self.cb3) 
        buttonBox.addWidget(fitButton) 
        
        vbl.addLayout(buttonBox)

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
    
    # handles loading a new plot
    def load_plot(self): 
        text, ok = QtGui.QInputDialog.getText(self, 'Open Dataset', 'Enter a dataset:')        
        if ok:
            #MR some type checking that is must be an integer. This won't be necessary when we switch to the browser.
            dataset = int(text)
        text2, ok = QtGui.QInputDialog.getText(self, 'Open Dataset', 'Enter a directory in labrad format:')        
        if ok:
            directory = tuple(eval(str(text2)))
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
        if (self.cb2.isChecked()):
            # "uncheck" the overlay checkbox
            self.cb2.toggle()
        # Remove this window from the dictionary so that no datasets...
        # ... are drawn to this window
        self.parent.removeWindowFromDictionary(self)

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
        text2, ok = QtGui.QInputDialog.getText(self, 'Open Dataset', 'Enter a directory in labrad format:')        
        if ok:
            directory = tuple(eval(str(text2)))
            #MR some type checking that is must be an integer. This won't be necessary when we switch to the browser.
            self.parent.newDataset(dataset, directory, self.manuallyLoaded)
