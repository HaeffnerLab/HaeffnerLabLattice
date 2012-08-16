from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks

class ExperimentGrid(QtGui.QTableWidget):
    def __init__(self, parent, experimentPath):
        QtGui.QTableWidget.__init__(self)
        self.parent = parent
        self.experimentPath = experimentPath
        self.parent.setWindowTitle(experimentPath[-1])
        self.setupExperimentGrid()
        self.setupExperimentParameterListener()

    @inlineCallbacks
    def setupExperimentGrid(self):
#        self.experimentGrid = QtGui.QGridLayout()
#        self.experimentGrid.setSpacing(5)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setColumnCount(2)

        self.checkBoxParameterDict = {}
        self.parameterCheckBoxDict = {}
        
        self.doubleSpinBoxParameterDict = {}
        self.parameterDoubleSpinBoxDict = {}

        self.lineEditParameterDict = {}
        self.parameterLineEditDict = {}        
        
        expParamNames = yield self.parent.server.get_parameter_names(self.experimentPath)
        
        self.setRowCount(len(expParamNames))
        
        Row = 0
        for parameter in expParamNames:
            # create a label and spin box, add it to the grid
            #label = QtGui.QLabel(parameter)
            item = QtGui.QTableWidgetItem(parameter)
            self.setItem(Row, 1, item)
            value = yield self.parent.server.get_parameter(self.experimentPath + [parameter])
            widget = self.parent.typeCheckerWidget(value)
            widgetType = type(widget)
            if (widgetType == QtGui.QCheckBox):
                self.checkBoxParameterDict[widget] = parameter
                self.parameterCheckBoxDict[parameter] = widget
                widget.stateChanged.connect(self.updateCheckBoxStateToSemaphore)   
                self.setCellWidget(Row, 0, widget)        
            elif (widgetType == QtGui.QDoubleSpinBox):
                self.doubleSpinBoxParameterDict[widget] = parameter
                self.parameterDoubleSpinBoxDict[parameter] = widget 
                widget.valueChanged.connect(self.updateSpinBoxValueToSemaphore)
#                self.connect(widget, QtCore.SIGNAL('valueChanged(double)'), self.updateSpinBoxValueToSemaphore)
                self.setCellWidget(Row, 0, widget)
            elif(widgetType == QtGui.QLineEdit):
                self.lineEditParameterDict[widget] = parameter
                self.parameterLineEditDict[parameter] = widget
                widget.editingFinished.connect(self.updateLineEditValueToSemaphore)                  
#                self.connect(widget, QtCore.SIGNAL('editingFinished()'), self.updateLineEditValueToSemaphore)
                self.setCellWidget(Row, 0, widget)
#            try:
#                if (len(value) == 3):
#                    doubleSpinBox = QtGui.QDoubleSpinBox()
#                    doubleSpinBox.setRange(value[0], value[1])
#                    doubleSpinBox.setValue(value[2])
#                    doubleSpinBox.setSingleStep(.1)
#                    doubleSpinBox.setKeyboardTracking(False)
#                                    
#                    self.doubleSpinBoxParameterDict[doubleSpinBox] = parameter
#                    self.parameterDoubleSpinBoxDict[parameter] = doubleSpinBox 
#                    
#                    self.connect(doubleSpinBox, QtCore.SIGNAL('valueChanged(double)'), self.updateSpinBoxValueToSemaphore)
#                    self.setCellWidget(Row, 0, doubleSpinBox)
#                else:
#                    raise                    
#                    
#    #                self.experimentGrid.addWidget(label, gridRow, gridCol, QtCore.Qt.AlignCenter)
#    #                self.experimentGrid.addWidget(doubleSpinBox, gridRow, gridCol + 1, QtCore.Qt.AlignCenter)
#            except:
#                lineEdit = QtGui.QLineEdit(readOnly=True)
#                #value = value[2:]
#                try:
#                    for i in range(len(value)):
#                        value[i] = value[i].value
#                except:
#                    pass #boolean!
#                lineEdit.setText(str(value))
#                        
#                self.lineEditParameterDict[lineEdit] = parameter
#                self.parameterLineEditDict[parameter] = lineEdit                  
#                
#                self.connect(lineEdit, QtCore.SIGNAL('editingFinished()'), self.updateLineEditValueToSemaphore)
#
#                self.setCellWidget(Row, 0, lineEdit)
                
#                self.experimentGrid.addWidget(label, gridRow, gridCol, QtCore.Qt.AlignCenter)
#                self.experimentGrid.addWidget(lineEdit, gridRow, gridCol + 1, QtCore.Qt.AlignCenter)

            
            Row += 1
#            gridCol += 2
#            if (gridCol == 6):
#                gridCol = 0
#                gridRow += 1
        
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
#        self.setLayout(self.experimentGrid)    
    
    @inlineCallbacks
    def setupExperimentParameterListener(self):
        context = self.parent.cxn.context()
        yield self.parent.cxn.semaphore.signal__parameter_change(22222, context = context)
        yield self.parent.cxn.semaphore.addListener(listener = self.updateExperimentParameter, source = None, ID = 22222, context = context)    

    def updateExperimentParameter(self, x, y):
        # need type checking here!
        if (y[0][:-1] == self.experimentPath):
            try:
                if (len(y[1]) == 3):
                    self.parameterDoubleSpinBoxDict[y[0][-1]].setValue(y[1][2])
            except:
                #boolean!
                pass
    

    @inlineCallbacks
    def updateCheckBoxStateToSemaphore(self, evt):
        yield self.parent.server.set_parameter(self.experimentPath + [self.checkBoxParameterDict[self.sender()]], bool(evt))
        
    @inlineCallbacks
    def updateSpinBoxValueToSemaphore(self, parameterValue):
        yield self.parent.server.set_parameter(self.experimentPath + [self.doubleSpinBoxParameterDict[self.sender()]], [self.sender().minimum(), self.sender().maximum(), parameterValue])
        
    @inlineCallbacks
    def updateLineEditValueToSemaphore(self):
        from labrad import types as T
        # two types....tuples [(value, unit)] or tuples of strings and values [(string, (value, unit))]
        value = eval(str(self.sender().text()))
        typeSecondElement = type(value[0][1])
        # normal list of labrad values
        if (typeSecondElement == str):
            # build a list of labrad values
            for i in range(len(value)):
                value[i] = T.Value(value[i][0], value[i][1])
        elif (typeSecondElement == tuple):
            for i in range(len(value)):
                value[i] = (value[i][0], T.Value[value[i][1][0]], value[i][1][1])
        yield self.parent.server.set_parameter(self.experimentPath + [self.lineEditParameterDict[self.sender()]], value)
