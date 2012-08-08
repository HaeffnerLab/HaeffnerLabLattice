from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks


class ExperimentGrid(QtGui.QWidget):
    def __init__(self, parent, experiment):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.experiment = experiment
        self.setupExperimentGrid()

    @inlineCallbacks
    def setupExperimentGrid(self):
        self.experimentGrid = QtGui.QGridLayout()
        self.experimentGrid.setSpacing(5)
        
        self.doubleSpinBoxDict = {}
        
        
        expParamNames = yield self.parent.server.get_experiment_parameter_names(self.experiment)
        expParamValues = yield self.parent.server.get_experiment_parameters(self.experiment, expParamNames)
        
        self.setupValueChangedDictionary(self.experiment, expParamNames)
        
        gridRow = 0
        gridCol = 0
        for parameter, value in zip(expParamNames, expParamValues):
            if ((parameter == 'Block') or (parameter == 'Continue') or (parameter == 'Status')):
                pass
            else:
                # create a label and spin box, add it to the grid
                label = QtGui.QLabel(parameter)
                doubleSpinBox = QtGui.QDoubleSpinBox()
                doubleSpinBox.setRange(-100000, 100000)
                doubleSpinBox.setValue(value)
                doubleSpinBox.setSingleStep(.1)
                doubleSpinBox.setKeyboardTracking(False)
                self.connect(doubleSpinBox, QtCore.SIGNAL('valueChanged(double)'), self.valueChangedDictionary[parameter])
                
                self.doubleSpinBoxDict[parameter] = doubleSpinBox
                
                self.experimentGrid.addWidget(label, gridRow, gridCol, QtCore.Qt.AlignCenter)
                self.experimentGrid.addWidget(doubleSpinBox, gridRow, gridCol + 1, QtCore.Qt.AlignCenter)
                
                gridCol += 2
                if (gridCol == 6):
                    gridCol = 0
                    gridRow += 1
        
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setLayout(self.experimentGrid)    
    
    def setupValueChangedDictionary(self, experiment, parameters):
        self.valueChangedDictionary = {}
        for parameter in parameters:
            @inlineCallbacks
            def func(value):
                yield self.parent.server.set_experiment_parameters(experiment, [parameter], [value])
            self.valueChangedDictionary[parameter] = func
