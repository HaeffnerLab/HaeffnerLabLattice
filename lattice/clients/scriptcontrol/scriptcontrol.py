import time
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from PyQt4 import QtGui, QtCore
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
        self.mainLayout = QtGui.QHBoxLayout()
        # mainGrid is in mainLayout that way its size can be controlled.
        self.mainGrid = QtGui.QGridLayout()
        self.mainGrid.setSpacing(5)
        
        self.mainLayout.addLayout(self.mainGrid)
        
        self.experimentListWidget = ExperimentListWidget(self)
        self.experimentListWidget.show()
        self.mainGrid.addWidget(self.experimentListWidget, 0, 0, QtCore.Qt.AlignCenter)
        
        # not this again!
        yield deferToThread(time.sleep, .05)
        self.setupExperimentGrid(['Test', 'Exp1'])
#       
#        parameterLimitsButton = QtGui.QPushButton("Parameter Limits", self)
#        parameterLimitsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
#        parameterLimitsButton.clicked.connect(self.parameterLimitsWindowEvent)
#        self.mainGrid.addWidget(parameterLimitsButton, 1, 1, QtCore.Qt.AlignCenter)
#        
        self.setupGlobalGrid(['Test', 'Exp1'])
#        
        self.setupStatusWidget(['Test', 'Exp1'])
        
        self.setLayout(self.mainLayout)
        self.show()


    def parameterLimitsWindowEvent(self, evt):
        experiment = self.experimentGrid.experiment
        try:
            self.parameterLimitsWindow.hide()
            del self.parameterLimitsWindow
            self.parameterLimitsWindow = ParameterLimitsWindow(self, experiment)
            self.parameterLimitsWindow.show()
        except:
            # first time
            self.parameterLimitsWindow = ParameterLimitsWindow(self, experiment)
            self.parameterLimitsWindow.show()

    def setupExperimentGrid(self, experiment):
        try:
            self.experimentGrid.hide()
        except:
            # First time
            pass
        self.experimentGrid = ExperimentGrid(self, experiment)           
        self.mainGrid.addWidget(self.experimentGrid, 0, 1, QtCore.Qt.AlignCenter)
        self.experimentGrid.show()  

    def setupGlobalGrid(self, experimentPath):
        try:
            self.globalGrid.hide()
        except:
            # First time
            pass
        self.globalGrid = GlobalGrid(self, experimentPath)           
        self.mainGrid.addWidget(self.globalGrid, 0, 2, QtCore.Qt.AlignCenter)
        self.globalGrid.show()          

    def setupStatusWidget(self, experiment):
        try:
            self.statusWidget.hide()
        except:
            # First time
            pass
        self.statusWidget = StatusWidget(self, experiment)           
        self.mainGrid.addWidget(self.statusWidget, 0, 3, QtCore.Qt.AlignCenter)
        self.statusWidget.show() 
        
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

