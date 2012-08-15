from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui, QtCore

class ParameterLimitsWindow(QtGui.QWidget):
    """Set Parameter Limits"""

    def __init__(self, parent, experimentPath):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.experimentPath = experimentPath
        self.setWindowTitle(self.experimentPath[-1])        
        self.setupWidget()
    
    def setupWidget(self):
        
        self.mainLayout = QtGui.QHBoxLayout()
        
        self.expParameterList = ExperimentParameterListWidget(self, self.experimentPath)
        self.mainLayout.addWidget(self.expParameterList)
        
        self.expParamLabel = QtGui.QLabel('')
        self.mainLayout.addWidget(self.expParamLabel)
        
        self.expParamLimitsEdit = QtGui.QLineEdit()
        self.connect(self.expParamLimitsEdit, QtCore.SIGNAL('editingFinished()'), self.updateExperimentParameterValue)
        self.mainLayout.addWidget(self.expParamLimitsEdit)
        
        self.globalParamLimitsEdit = QtGui.QLineEdit()
        self.connect(self.globalParamLimitsEdit, QtCore.SIGNAL('editingFinished()'), self.updateGlobalParameterValue)
        self.mainLayout.addWidget(self.globalParamLimitsEdit)
        
        self.globalParamLabel = QtGui.QLabel('')
        self.mainLayout.addWidget(self.globalParamLabel)

        self.globalParameterList = GlobalParameterListWidget(self, self.experimentPath)
        self.mainLayout.addWidget(self.globalParameterList)

        
        self.setLayout(self.mainLayout)
        


    @inlineCallbacks
    def updateExperimentParameterValue(self):
        currentParameter = str(self.expParamLabel.text())
        value = yield self.parent.server.get_parameter(self.experimentPath + [currentParameter])
        limits = eval(str(self.expParamLimitsEdit.text()))
        value[0] = float(limits[0])
        value[1] = float(limits[1])
        yield self.parent.server.set_parameter(self.experimentPath + [currentParameter], value)
        self.parent.experimentGrid.parameterDoubleSpinBoxDict[currentParameter].setRange(value[0], value[1])
        #update the spinBox
 
 
    # NEED A WAY TO keep track of globals like in globalgrid!!
    @inlineCallbacks
    def updateGlobalParameterValue(self):
        currentParameter = str(self.globalParamLabel.text())
        value = yield self.parent.server.get_parameter(self.parent.globalGrid.globalParameterDict[currentParameter])
        limits = eval(str(self.globalParamLimitsEdit.text()))
        value[0] = float(limits[0])
        value[1] = float(limits[1])
        yield self.parent.server.set_parameter(self.parent.globalGrid.globalParameterDict[currentParameter], value)
        self.parent.globalGrid.parameterDoubleSpinBoxDict[currentParameter].setRange(value[0], value[1])
   
    @inlineCallbacks
    def loadExperimentParameterLimits(self, parameter):
        value = yield self.parent.server.get_parameter(self.experimentPath + [parameter])
        self.expParamLabel.setText(parameter)
        self.expParamLimitsEdit.setText('['+str(value[0])+','+str(value[1])+']')

    @inlineCallbacks
    def loadGlobalParameterLimits(self, parameter):
        value = yield self.parent.server.get_parameter(self.parent.globalGrid.globalParameterDict[parameter])
        self.globalParamLabel.setText(parameter)
        self.globalParamLimitsEdit.setText('['+str(value[0])+','+str(value[1])+']')

    
    def closeEvent(self, evt):
        self.hide()
 
 
class ExperimentParameterListWidget(QtGui.QListWidget):

    def __init__(self, parent, experimentPath):
        QtGui.QListWidget.__init__(self)
        self.parent = parent
        self.experimentPath = experimentPath
        self.setupWidget()
        
    @inlineCallbacks
    def setupWidget(self):
        expParamNames = yield self.parent.parent.server.get_parameter_names(self.experimentPath)
        for parameter in expParamNames:
            self.addItem(parameter)
        
        self.parent.loadExperimentParameterLimits(expParamNames[0])
        
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
    def mousePressEvent(self, event):
        """
        mouse clicks events
        """
        button = event.button()
        item = self.itemAt(event.x(), event.y())
        if item:
            if (button == 1):
                self.parent.loadExperimentParameterLimits(str(item.text()))
                
class GlobalParameterListWidget(QtGui.QListWidget):

    def __init__(self, parent, experimentPath):
        QtGui.QListWidget.__init__(self)
        self.parent = parent
        self.experimentPath = experimentPath
        self.setupWidget()
        
    def setupWidget(self):
        globalParamNames = self.parent.parent.globalGrid.globalParameterDict.keys()
        for parameter in globalParamNames:
            self.addItem(parameter)
        
        self.parent.loadGlobalParameterLimits(globalParamNames[0])
        
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
    def mousePressEvent(self, event):
        """
        mouse clicks events
        """
        button = event.button()
        item = self.itemAt(event.x(), event.y())
        if item:
            if (button == 1):
                self.parent.loadGlobalParameterLimits(str(item.text()))