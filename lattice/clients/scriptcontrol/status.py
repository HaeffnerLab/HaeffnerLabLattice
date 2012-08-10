from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread

class StatusWidget(QtGui.QWidget):
    def __init__(self, parent, experiment):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.experiment = experiment
        
        self.mainLayout = QtGui.QVBoxLayout()
        
        self.createStatusLabel()
        
        self.startButton = QtGui.QPushButton("New", self)
        self.startButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        self.startButton.clicked.connect(self.startButtonSignal)
        self.mainLayout.addWidget(self.startButton)
        
        self.pauseContinueButton = QtGui.QPushButton("Pause", self)
        self.pauseContinueButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        self.pauseContinueButton.clicked.connect(self.pauseContinueButtonSignal)
        self.mainLayout.addWidget(self.pauseContinueButton)
        
        self.stopButton = QtGui.QPushButton("Stop", self)
        self.stopButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        self.stopButton.clicked.connect(self.stopButtonSignal)
        self.mainLayout.addWidget(self.stopButton)
        
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setLayout(self.mainLayout)
    
    @inlineCallbacks
    def createStatusLabel(self):
        status = yield self.parent.server.get_general_experiment_parameter(self.experiment, 'Status')
        self.statusLabel = QtGui.QLabel(status)
        self.mainLayout.addWidget(self.statusLabel)

    @inlineCallbacks
    def startButtonSignal(self, evt):
        yield self.parent.cxn.semaphore.set_general_experiment_parameter(self.experiment, 'Continue', True)
        yield self.parent.cxn.semaphore.set_general_experiment_parameter(self.experiment, 'Block', False)
        yield self.parent.cxn.semaphore.set_general_experiment_parameter(self.experiment, 'Status', 'Running')
        yield deferToThread(self.parent.experiments[self.experiment].run)
        #self.startButton.setDisabled(True)
        #self.stopButton.setEnabled(True)
        
    @inlineCallbacks
    def pauseContinueButtonSignal(self, evt):
        status = yield self.parent.server.get_general_experiment_parameter(self.experiment, 'Status')
        if (status == 'Running'):
            yield self.parent.cxn.semaphore.set_general_experiment_parameter(self.experiment, 'Block', True)
            yield self.parent.cxn.semaphore.set_general_experiment_parameter(self.experiment, 'Status', 'Paused')
        elif (status == 'Paused'):
            yield self.parent.cxn.semaphore.set_general_experiment_parameter(self.experiment, 'Block', False)
            yield self.parent.cxn.semaphore.set_general_experiment_parameter(self.experiment, 'Status', 'Running')
    
    @inlineCallbacks
    def stopButtonSignal(self, evt):
        status = yield self.parent.server.get_general_experiment_parameter(self.experiment, 'Status')
        if (status == 'Paused'):
            yield self.parent.cxn.semaphore.set_general_experiment_parameter(self.experiment, 'Block', False)
        yield self.parent.cxn.semaphore.set_general_experiment_parameter(self.experiment, 'Continue', False)
        yield self.parent.cxn.semaphore.set_general_experiment_parameter(self.experiment, 'Status', 'Stopped')
        #self.stopButton.setDisabled(True)
        #self.startButton.setEnabled(True)