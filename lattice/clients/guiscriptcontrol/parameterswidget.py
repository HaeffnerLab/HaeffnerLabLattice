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
#        try:
#            self.experimentGrid.setupExperimentGrid(experimentPath, self.experimentContext)
#            self.experimentGridLayout.addWidget(self.experimentParametersLabel)
#            self.experimentGridLayout.setAlignment(self.experimentParametersLabel, QtCore.Qt.AlignCenter)
#            self.experimentGridLayout.setStretchFactor(self.experimentParametersLabel, 0)
#            self.experimentGridLayout.addWidget(self.experimentGrid)
##            self.experimentGrid.disconnectSignal()
##            self.experimentGrid.hide()
##            del self.experimentGrid
#        except:
#            # First time
        self.experimentGrid = ExperimentGrid(self, experimentPath, self.experimentContext)
        self.experimentGridLayout.addWidget(self.experimentParametersLabel)
        self.experimentGridLayout.setAlignment(self.experimentParametersLabel, QtCore.Qt.AlignCenter)
        self.experimentGridLayout.setStretchFactor(self.experimentParametersLabel, 0)
        self.experimentGridLayout.addWidget(self.experimentGrid)         
        self.setupExperimentGrid = self.setupExperimentGridSubsequent
#        self.experimentGrid = ExperimentGrid(self, experimentPath, self.experimentContext)

        self.experimentGrid.show()  

    @inlineCallbacks
    def setupExperimentGridSubsequent(self, experimentPath):
        yield self.experimentGrid.setupExperimentGrid(experimentPath)
       

    def setupGlobalGrid(self, experimentPath):
        self.globalGrid = GlobalGrid(self, experimentPath, self.globalContext)
        self.globalGridLayout.addWidget(self.globalParametersLabel)
        self.globalGridLayout.setAlignment(self.globalParametersLabel, QtCore.Qt.AlignCenter)
        self.globalGridLayout.setStretchFactor(self.globalParametersLabel, 0)
        self.globalGridLayout.addWidget(self.globalGrid)            
#            self.globalGrid.disconnectSignal()
#            self.globalGrid.hide()
#            del self.globalGrid

            # First time

#        self.globalGrid.show()  
        self.setupGlobalGrid = self.setupGlobalGridSubsequent          
        
    def setupGlobalGridSubsequent(self, experimentPath):
        self.globalGrid.setupGlobalGrid(experimentPath)        
    
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