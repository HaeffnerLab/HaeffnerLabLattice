import time
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from PyQt4 import QtGui, QtCore
from experimentlist import ExperimentListWidget
from experimentgrid import ExperimentGrid


class ScriptControl(QtGui.QWidget):
    def __init__(self,reactor, parent=None):
        QtGui.QWidget.__init__(self)
        self.reactor = reactor
        self.experiments = ['Test', 'Test2']
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync()
        self.server = self.cxn.semaphore
        self.server.initialize_experiments(self.experiments)
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
        
        self.setLayout(self.mainLayout)
        self.show()
        # not this again!
        yield deferToThread(time.sleep, .05)
        self.setupExperimentGrid(self.experiments[0])

    def setupExperimentGrid(self, experiment):
        try:
            self.experimentGrid.hide()
        except:
            # First time
            pass
        self.experimentGrid = ExperimentGrid(self, experiment)           
        self.mainGrid.addWidget(self.experimentGrid, 0, 1, QtCore.Qt.AlignCenter)
        self.experimentGrid.show()  
        

    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    scriptControl = ScriptControl(reactor)
    reactor.run()

