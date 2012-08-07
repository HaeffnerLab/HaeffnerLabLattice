import time
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from PyQt4 import QtGui, QtCore
from experimentlist import ExperimentListWidget


class ScriptControl(QtGui.QWidget):
    def __init__(self,reactor, parent=None):
        QtGui.QWidget.__init__(self)
        self.reactor = reactor
        self.experiments = ['Test']
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync()
        self.server = self.cxn.semaphore
        self.setupMainWidget()
        
    def setupMainWidget(self):
        self.mainLayout = QtGui.QHBoxLayout()
        # mainGrid is in mainLayout that way its size can be controlled.
        self.mainGrid = QtGui.QGridLayout()
        self.mainGrid.setSpacing(5)
        
        self.mainLayout.addLayout(self.mainGrid)
        
        self.experimentListWidget = ExperimentListWidget(self)
        self.experimentListWidget.show()
        self.mainGrid.addWidget(self.experimentListWidget, 0, 0, QtCore.Qt.AlignCenter)
        
        
        self.setLayout(self.mainLayout)
        self.show()

    @inlineCallbacks    
    def setupExperimentGrid(self, experiment):
        self.experimentGrid = QtGui.QGridLayout()
        self.experimentGrid.setSpacing(5)
        
        self.doubleSpinBoxDict = {}
        
        
        expParamNames = yield self.server.get_experiment_parameter_names(experiment)
        expParamValues = yield self.server.get_experiment_parameters(experiment, expParamNames)
        
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
                doubleSpinBox.setSingleStep(.1)
                
                self.doubleSpinBoxDict[parameter] = doubleSpinBox
                
                self.experimentGrid.addWidget(label, gridRow, gridCol, QtCore.Qt.AlignCenter)
                self.experimentGrid.addWidget(doubleSpinBox, gridRow, gridCol + 1, QtCore.Qt.AlignCenter)
                
                gridCol += 2
                if (gridCol == 6):
                    gridCol = 0
                    gridRow += 1
                    
        self.experimentGrid.show()     
                
#            if (i % 2 == 0): #even
#                grid.addWidget(devPanel, (i / 2) , 0)
#            else:
#                grid.addWidget(devPanel, ((i - 1) / 2) , 1)
        
        

        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        self.show()

    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    scriptControl = ScriptControl(reactor)
    reactor.run()

