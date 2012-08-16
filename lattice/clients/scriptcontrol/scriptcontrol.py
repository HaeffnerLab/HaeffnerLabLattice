import time
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from PyQt4 import QtGui, QtCore
import re
from experimentlist import ExperimentListWidget
from experimentgrid import ExperimentGrid
from globalgrid import GlobalGrid
from parameterlimitswindow import ParameterLimitsWindow
from status import StatusWidget
from experiments.Test import Test
from experiments.Test2 import Test2



class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    
    def __setitem__(self, key, val):
        self.__dict__[key] = val
    
    def toDict(self):
        return self.__dict__

class ScriptControl(QtGui.QWidget):
    def __init__(self,reactor, parent=None):
        QtGui.QWidget.__init__(self)
        self.reactor = reactor
        self.experiments = {
                            str(['Test', 'Exp1']):  Test(),
                            str(['Test', 'Exp2']):  Test2()
                           }
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync()
        self.server = self.cxn.semaphore
#        self.server.initialize_experiments(self.experiments.keys())
        self.setupMainWidget()
        
    @inlineCallbacks
    def setupMainWidget(self):
        
        # contexts
        self.experimentContext = yield self.cxn.context()
        self.globalContext = yield self.cxn.context()
        self.statusContext = yield self.cxn.context()
        
        self.mainLayout = QtGui.QHBoxLayout()
        # mainGrid is in mainLayout that way its size can be controlled.
        self.mainGrid = QtGui.QGridLayout()
        self.mainGrid.setSpacing(5)
        font = QtGui.QFont('MS Shell Dlg 2',pointSize=14)
        font.setUnderline(True)
        experimentListLabel = QtGui.QLabel('Experiment Navigation')
        experimentListLabel.setFont(font)
        experimentParametersLabel = QtGui.QLabel('Experiment Parameters')
        experimentParametersLabel.setFont(font)
        globalParametersLabel = QtGui.QLabel('Global Parameters')
        globalParametersLabel.setFont(font)
        controlLabel = QtGui.QLabel('Control')
        controlLabel.setFont(font)
                
        self.mainGrid.addWidget(experimentListLabel, 0, 0, QtCore.Qt.AlignCenter)
        self.mainGrid.addWidget(experimentParametersLabel, 0, 1, QtCore.Qt.AlignCenter)
        self.mainGrid.addWidget(globalParametersLabel, 0, 2, QtCore.Qt.AlignCenter)
        self.mainGrid.addWidget(controlLabel, 0, 3, QtCore.Qt.AlignCenter)        
        
        self.mainLayout.addLayout(self.mainGrid)
        
        self.experimentListWidget = ExperimentListWidget(self)
        self.experimentListWidget.show()
        self.mainGrid.addWidget(self.experimentListWidget, 1, 0, QtCore.Qt.AlignCenter)
        
        # not this again!
        yield deferToThread(time.sleep, .05)
        self.setupExperimentGrid(['Test', 'Exp1'])
#       
        parameterLimitsButton = QtGui.QPushButton("Parameter Limits", self)
        parameterLimitsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        parameterLimitsButton.clicked.connect(self.parameterLimitsWindowEvent)
        self.mainGrid.addWidget(parameterLimitsButton, 2, 1, QtCore.Qt.AlignCenter)
#        
        self.setupGlobalGrid(['Test', 'Exp1'])
#        
        self.setupStatusWidget(['Test', 'Exp1'])
        
        self.setLayout(self.mainLayout)
        self.show()


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

    def setupExperimentGrid(self, experimentPath):
        try:
            self.experimentGrid.hide()
        except:
            # First time
            pass
        self.experimentGrid = ExperimentGrid(self, experimentPath, self.experimentContext)           
        self.mainGrid.addWidget(self.experimentGrid, 1, 1, QtCore.Qt.AlignCenter)
        self.experimentGrid.show()  

    def setupGlobalGrid(self, experimentPath):
        try:
            self.globalGrid.hide()
        except:
            # First time
            pass
        self.globalGrid = GlobalGrid(self, experimentPath, self.globalContext)           
        self.mainGrid.addWidget(self.globalGrid, 1, 2, QtCore.Qt.AlignCenter)
        self.globalGrid.show()          

    def setupStatusWidget(self, experiment):
        try:
            self.statusWidget.hide()
        except:
            # First time
            pass
        self.statusWidget = StatusWidget(self, experiment, self.statusContext)           
        self.mainGrid.addWidget(self.statusWidget, 1, 3, QtCore.Qt.AlignCenter)
        self.statusWidget.show() 
        
    def typeCheckerWidget(self, Value):
        
        # boolean
        if (type(Value) == bool):
            checkbox = QtGui.QCheckBox()
            if (Value == True):
                checkbox.toggle()
            return checkbox
        else:
            value = Value.aslist
        
        
        # [min, max, value] gets a spinbox
        if ((type(value) == list) and (len(value) == 3)):
            doubleSpinBox = QtGui.QDoubleSpinBox()
            doubleSpinBox.setRange(value[0], value[1])
            number_dec = len(str(value[0]-int(value[0]))[2:])
            doubleSpinBox.setDecimals(number_dec + 1)
            doubleSpinBox.setValue(value[2])
            doubleSpinBox.setSuffix(value[2].units)
            doubleSpinBox.setSingleStep(.1)
            doubleSpinBox.setKeyboardTracking(False)
            doubleSpinBox.setMouseTracking(False)
            # for decimals...take minimum value, add one more digit
            return doubleSpinBox
        # list with more or less than 3 values
        else:
            lineEdit = QtGui.QLineEdit()
        
#            # list of floats
#            listElementType = type(value[0]) # enough to just check the first time, these should be homogenous. 
#            from labrad.units import Value as labradValue
#            if (listElementType == labradValue):
#                for i in range(len(value)):
#                    value[i] = value[i].value
#            # list of tuples
#            elif (listElementType == tuple):
#                # not sure what to do here yet
#                pass
            text = str(value)
            text = re.sub('Value', '', text)
            lineEdit.setText(text)
            return lineEdit
                    
        
    @inlineCallbacks
    def saveParametersToRegistryAndQuit(self):
        success = yield self.server.save_parameters_to_registry()
        if (success == True):
            print 'Current Parameters Saved Successfully.'
        self.reactor.stop()
                
    def closeEvent(self, x):
        self.saveParametersToRegistryAndQuit()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    scriptControl = ScriptControl(reactor)
    reactor.run()

