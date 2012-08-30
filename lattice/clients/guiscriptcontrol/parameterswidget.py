from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks
from experimentgrid import ExperimentGrid
from globalgrid import GlobalGrid
from parameterlimitswindow import ParameterLimitsWindow

class ParametersWidget(QtGui.QWidget):
#    def __init__(self, parent, experimentContext, globalContext):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        
        self.mainLayout = QtGui.QVBoxLayout()
        
        font = QtGui.QFont('MS Shell Dlg 2',pointSize=14)
        font.setUnderline(True)
        self.experimentParametersLabel = QtGui.QLabel('Experiment Parameters')
        self.experimentParametersLabel.setFont(font)
        self.globalParametersLabel = QtGui.QLabel('Global Parameters')
        self.globalParametersLabel.setFont(font)        
        
        # Setup Experiment Parameter Widget
        self.widgetsLayout = QtGui.QHBoxLayout()
        self.miscLayout = QtGui.QHBoxLayout()
        
        self.experimentGridLayout = QtGui.QVBoxLayout()
#        self.setupExperimentGrid(['Test', 'Exp1']) # the experiment to start with
        # Setup Global Parameter Widget
        self.globalGridLayout = QtGui.QVBoxLayout()      
#        self.setupGlobalGrid(['Test', 'Exp1']) # the experiment to start with  
        
        self.widgetsLayout.addLayout(self.experimentGridLayout)
        self.widgetsLayout.addLayout(self.globalGridLayout)
        
        parameterLimitsButton = QtGui.QPushButton("Parameter Limits", self)
        parameterLimitsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        parameterLimitsButton.clicked.connect(self.parameterLimitsWindowEvent)
        self.miscLayout.addWidget(parameterLimitsButton)
        
        self.mainLayout.addLayout(self.widgetsLayout)
        self.mainLayout.addLayout(self.miscLayout)
        
        self.setLayout(self.mainLayout)
        self.show()

    def setContexts(self, experimentContext, globalContext):
        self.experimentContext = experimentContext
        self.globalContext = globalContext
        self.setupExperimentGrid(['Test', 'Exp1'])
        self.setupGlobalGrid(['Test', 'Exp1'])      

    def setupExperimentGrid(self, experimentPath):
        try:
            self.experimentGrid.hide()
        except:
            # First time
            pass
        self.experimentGrid = ExperimentGrid(self, experimentPath, self.experimentContext)
        self.experimentGridLayout.addWidget(self.experimentParametersLabel)
        self.experimentGridLayout.setAlignment(self.experimentParametersLabel, QtCore.Qt.AlignCenter)
        self.experimentGridLayout.setStretchFactor(self.experimentParametersLabel, 0)
        self.experimentGridLayout.addWidget(self.experimentGrid)
        self.experimentGrid.show()  

    def setupGlobalGrid(self, experimentPath):
        try:
            self.globalGrid.hide()
        except:
            # First time
            pass
        self.globalGrid = GlobalGrid(self, experimentPath, self.globalContext)
        self.globalGridLayout.addWidget(self.globalParametersLabel)
        self.globalGridLayout.setAlignment(self.globalParametersLabel, QtCore.Qt.AlignCenter)
        self.globalGridLayout.setStretchFactor(self.globalParametersLabel, 0)
        self.globalGridLayout.addWidget(self.globalGrid)
        self.globalGrid.show()            
        
    def parameterLimitsWindowEvent(self, evt):
        experimentPath = self.experimentGrid.experimentPath
        try:
            self.parameterLimitsWindow.hide()
            del self.parameterLimitsWindow
            self.parameterLimitsWindow = ParameterLimitsWindow(self, experimentPath)
            self.parameterLimitsWindow.show()
        except:
            # first time
            self.parameterLimitsWindow = ParameterLimitsWindow(self, experimentPath)
            self.parameterLimitsWindow.show()        