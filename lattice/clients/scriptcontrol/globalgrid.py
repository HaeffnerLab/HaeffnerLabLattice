from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks

class GlobalGrid(QtGui.QWidget):
    def __init__(self, parent, experimentPath):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.experimentPath = experimentPath
        self.setupGlobalGrid()
        self.setupGlobalParameterListener()

    @inlineCallbacks
    def setupGlobalGrid(self):
        self.globalGrid = QtGui.QGridLayout()
        self.globalGrid.setSpacing(5)
        
        self.doubleSpinBoxParameterDict = {}
        self.parameterDoubleSpinBoxDict = {}
        self.globalParameterDict = {}
        
        path = self.experimentPath
        for i in range(len(self.experimentPath)):
            path = path[:-1]
            paramNames = yield self.parent.server.get_parameter_names(path)
            for paramName in paramNames:
                self.globalParameterDict[paramName] = path + [paramName]
        
        gridRow = 0
        gridCol = 0
        for parameter in self.globalParameterDict.keys():
            # create a label and spin box, add it to the grid
            value = yield self.parent.server.get_parameter(self.globalParameterDict[parameter])
            label = QtGui.QLabel(parameter)
            doubleSpinBox = QtGui.QDoubleSpinBox()
            doubleSpinBox.setRange(value[0], value[1])
            doubleSpinBox.setValue(value[2])
            doubleSpinBox.setSingleStep(.1)
            doubleSpinBox.setKeyboardTracking(False)
            self.connect(doubleSpinBox, QtCore.SIGNAL('valueChanged(double)'), self.updateValueToSemaphore)
            
            self.doubleSpinBoxParameterDict[doubleSpinBox] = parameter
            self.parameterDoubleSpinBoxDict[parameter] = doubleSpinBox
            
            self.globalGrid.addWidget(label, gridRow, gridCol, QtCore.Qt.AlignCenter)
            self.globalGrid.addWidget(doubleSpinBox, gridRow, gridCol + 1, QtCore.Qt.AlignCenter)
            
            gridCol += 2
            if (gridCol == 6):
                gridCol = 0
                gridRow += 1
        
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setLayout(self.globalGrid)    

    @inlineCallbacks
    def setupGlobalParameterListener(self):
        yield self.parent.cxn.semaphore.signal__parameter_change(33333)#, context = context)
        yield self.parent.cxn.semaphore.addListener(listener = self.updateGlobalParameter, source = None, ID = 33333)#, context = context)    

    def updateGlobalParameter(self, x, y):
        print 'experiment signal!'
        print x, y        
#        self.parameterDoubleSpinBoxDict[y[0]].setValue(y[1])
    
    @inlineCallbacks
    def updateValueToSemaphore(self, parameterValue):
        yield self.parent.server.set_parameter(self.globalParameterDict[self.doubleSpinBoxParameterDict[self.sender()]], [self.sender().minimum(), self.sender().maximum(), parameterValue])
