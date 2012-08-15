from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks

class ExperimentGrid(QtGui.QWidget):
    def __init__(self, parent, experimentPath):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.experimentPath = experimentPath
        self.parent.setWindowTitle(experimentPath[-1])
        self.setupExperimentGrid()
        self.setupExperimentParameterListener()

    @inlineCallbacks
    def setupExperimentGrid(self):
        self.experimentGrid = QtGui.QGridLayout()
        self.experimentGrid.setSpacing(5)
        
        self.doubleSpinBoxParameterDict = {}
        self.parameterDoubleSpinBoxDict = {}
        
        expParamNames = yield self.parent.server.get_parameter_names(self.experimentPath)
        
        gridRow = 0
        gridCol = 0
        for parameter in expParamNames:
            # create a label and spin box, add it to the grid
            value = yield self.parent.server.get_parameter(self.experimentPath + [parameter])
            label = QtGui.QLabel(parameter)
            doubleSpinBox = QtGui.QDoubleSpinBox()
            doubleSpinBox.setRange(value[0], value[1])
            doubleSpinBox.setValue(value[2])
            doubleSpinBox.setSingleStep(.1)
            doubleSpinBox.setKeyboardTracking(False)
            self.connect(doubleSpinBox, QtCore.SIGNAL('valueChanged(double)'), self.updateValueToSemaphore)
            
            self.doubleSpinBoxParameterDict[doubleSpinBox] = parameter
            self.parameterDoubleSpinBoxDict[parameter] = doubleSpinBox 
            
            self.experimentGrid.addWidget(label, gridRow, gridCol, QtCore.Qt.AlignCenter)
            self.experimentGrid.addWidget(doubleSpinBox, gridRow, gridCol + 1, QtCore.Qt.AlignCenter)
            
            gridCol += 2
            if (gridCol == 6):
                gridCol = 0
                gridRow += 1
        
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setLayout(self.experimentGrid)    
    
    @inlineCallbacks
    def setupExperimentParameterListener(self):
        yield self.parent.cxn.semaphore.signal__parameter_change(22222)#, context = context)
        yield self.parent.cxn.semaphore.addListener(listener = self.updateExperimentParameter, source = None, ID = 22222)#, context = context)    

    def updateExperimentParameter(self, x, y):
        print 'experiment signal!'
        print x, y
#        if (y[0] == self.experimentPath):
#            self.parameterDoubleSpinBoxDict[y[1]].setValue(y[2])

    
    @inlineCallbacks
    def updateValueToSemaphore(self, parameterValue):
        yield self.parent.server.set_parameter(self.experimentPath + [self.doubleSpinBoxParameterDict[self.sender()]], [self.sender().minimum(), self.sender().maximum(), parameterValue])
