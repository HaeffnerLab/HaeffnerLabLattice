from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread

class StatusWidget(QtGui.QWidget):
    def __init__(self, parent, experimentPath):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.experimentPath = experimentPath
        
        self.mainLayout = QtGui.QVBoxLayout()
        
        self.createStatusLabel()
        
        self.setupStatusListener()
        
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
        status = yield self.parent.server.get_parameter(self.experimentPath + ['Semaphore', 'Status'])
        self.statusLabel = QtGui.QLabel(status)
        self.mainLayout.addWidget(self.statusLabel)
        if (self.statusLabel.text() == 'Paused'):
            self.startButton.setDisabled(True)
            self.pauseContinueButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.pauseContinueButton.setText('Continue')
        elif (self.statusLabel.text() == 'Running'):            
            self.startButton.setDisabled(True)
            self.stopButton.setEnabled(True)
            self.pauseContinueButton.setEnabled(True)
            self.pauseContinueButton.setText('Pause')
        else:
            self.pauseContinueButton.setDisabled(True)    
            self.stopButton.setDisabled(True)
            self.startButton.setEnabled(True)
                
    @inlineCallbacks
    def setupStatusListener(self):
        yield self.parent.cxn.semaphore.signal__parameter_change(11111)#, context = context)
        yield self.parent.cxn.semaphore.addListener(listener = self.updateStatus, source = None, ID = 11111)#, context = context)    
    
    def updateStatus(self, x, y):
        print x, y
#        self.statusLabel.setText(y[1])

    @inlineCallbacks
    def startButtonSignal(self, evt):
        self.startButton.setDisabled(True)
        self.stopButton.setEnabled(True)  
        self.pauseContinueButton.setEnabled(True)      
        yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Continue'], True)
        yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Block'], False)
        yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Status'], 'Running')
        self.statusLabel.setText('Running')
        yield deferToThread(self.parent.experiments[str(self.experimentPath)].run)

        
    @inlineCallbacks
    def pauseContinueButtonSignal(self, evt):
        status = yield self.parent.server.get_parameter(self.experimentPath + ['Semaphore', 'Status'])
        if (status == 'Running'):
            yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Block'], True)
            yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Status'], 'Paused')
            self.pauseContinueButton.setText('Continue')
            self.statusLabel.setText('Paused')
        elif (status == 'Paused'):
            yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Block'], False)
            yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Status'], 'Running')
            self.pauseContinueButton.setText('Pause')
            self.statusLabel.setText('Running')
    
    @inlineCallbacks
    def stopButtonSignal(self, evt):
        self.stopButton.setDisabled(True)
        self.startButton.setEnabled(True)    
        self.pauseContinueButton.setDisabled(True)    
        status = yield self.parent.server.get_parameter(self.experimentPath + ['Semaphore', 'Status'])
        if (status == 'Paused'):
            yield self.parent.server.set_parameter(self.experimentPath + ['Semaphore', 'Block'], False)
        yield self.parent.server.set_parameter(self.experimentPath + ['Semaphore', 'Continue'], False)
        yield self.parent.server.set_parameter(self.experimentPath + ['Semaphore', 'Status'], 'Stopped')
        self.pauseContinueButton.setText('Pause')
        self.statusLabel.setText('Stopped')
