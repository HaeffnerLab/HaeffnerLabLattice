from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread

class StatusWidget(QtGui.QWidget):
    def __init__(self, parent, experimentPath, context):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.context = context
        self.experimentPath = experimentPath
        
        self.mainLayout = QtGui.QVBoxLayout()
        
        self.createStatusLabel()
        
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setLayout(self.mainLayout)
    
    @inlineCallbacks
    def createStatusLabel(self):
        if (tuple(self.experimentPath) in self.parent.experiments.keys()):
            
            status = yield self.parent.server.get_parameter(self.experimentPath + ['Semaphore', 'Status'])
            
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
            
            self.statusLabel = QtGui.QLabel(status)
            self.statusLabel.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))
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
            elif(self.statusLabel.text() == 'Pausing'):
                self.startButton.setDisabled(True)
                self.pauseContinueButton.setEnabled(True)
                self.stopButton.setEnabled(True)
                self.pauseContinueButton.setText('Continue')              
            elif (status == 'Stopping'):
                self.startButton.setDisabled(True)                
                self.pauseContinueButton.setDisabled(True)    
                self.stopButton.setDisabled(True)
            else:
                self.pauseContinueButton.setDisabled(True)    
                self.stopButton.setDisabled(True)
                self.startButton.setEnabled(True)

            self.pbar = QtGui.QProgressBar()
            self.pbar.setValue(self.parent.experimentProgressDict[tuple(self.experimentPath)])
            self.mainLayout.addWidget(self.pbar)   
            
            self.setupStatusListener()               

        else:
            self.statusLabel = QtGui.QLabel('No Script Loaded For This Experiment')
            self.mainLayout.addWidget(self.statusLabel)
                            
    @inlineCallbacks
    def setupStatusListener(self):
        yield self.parent.cxn.semaphore.signal__parameter_change(11111, context = self.context)
        yield self.parent.cxn.semaphore.addListener(listener = self.updateStatus, source = None, ID = 11111, context = self.context)    
    
    @inlineCallbacks
    def updateStatus(self, x, y):
        if (y[0][:-2] == self.experimentPath):
            if (y[0][-1] == 'Status'):
                parameter = yield self.parent.server.get_parameter(self.experimentPath + ['Semaphore', 'Status'] , context = self.context)
                if (parameter == 'Finished' or parameter == 'Stopped'):
                    self.statusLabel.setText(y[1])
                    self.stopButton.setDisabled(True)
                    self.startButton.setEnabled(True)    
                    self.pauseContinueButton.setDisabled(True)
                    self.pauseContinueButton.setText('Pause')
                    yield self.parent.server.set_parameter(self.experimentPath + ['Semaphore', 'Continue'], True, context = self.context)
                elif (parameter == 'Paused'):
                    self.statusLabel.setText(parameter)
            elif (y[0][-1] == 'Progress'):
                self.parent.experimentProgressDict[tuple(self.experimentPath)] = y[1]
                self.pbar.setValue(y[1])
        yield None
            
    @inlineCallbacks
    def startButtonSignal(self, evt):
        self.startButton.setDisabled(True)
        self.stopButton.setEnabled(True)  
        self.pauseContinueButton.setEnabled(True)      
        yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Continue'], True, context = self.context)
        yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Block'], False, context = self.context)
        yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Status'], 'Running', context = self.context)
        self.statusLabel.setText('Running')
        self.parent.startExperiment(tuple(self.experimentPath))
        
    @inlineCallbacks
    def pauseContinueButtonSignal(self, evt):
        status = yield self.parent.server.get_parameter(self.experimentPath + ['Semaphore', 'Status'])
        if (status == 'Running'):
            yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Status'], 'Pausing', context = self.context)
#            yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Block'], True, context = self.context)
            self.pauseContinueButton.setText('Continue')
            self.statusLabel.setText('Pausing')
        elif (status == 'Paused' or status == 'Pausing'):
            yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Block'], False, context = self.context)
            yield self.parent.cxn.semaphore.set_parameter(self.experimentPath + ['Semaphore', 'Status'], 'Running', context = self.context)
            self.pauseContinueButton.setText('Pause')
            self.statusLabel.setText('Running')

    @inlineCallbacks
    def stopButtonSignal(self, evt):
        self.stopButton.setDisabled(True)
        self.startButton.setDisabled(True)    
        self.pauseContinueButton.setDisabled(True)    
        status = yield self.parent.server.get_parameter(self.experimentPath + ['Semaphore', 'Status'])
        if (status == 'Paused' or status == 'Pausing'):
            yield self.parent.server.set_parameter(self.experimentPath + ['Semaphore', 'Block'], False, context = self.context)
        yield self.parent.server.set_parameter(self.experimentPath + ['Semaphore', 'Continue'], False, context = self.context)
        yield self.parent.server.set_parameter(self.experimentPath + ['Semaphore', 'Status'], 'Stopping', context = self.context)
        self.pauseContinueButton.setText('Pause')
        self.statusLabel.setText('Stopping')  
    
    def handleScriptError(self, e):
        self.stopButton.setDisabled(True)
        self.startButton.setEnabled(True)    
        self.pauseContinueButton.setDisabled(True)    
        self.pauseContinueButton.setText('Pause')
        self.statusLabel.setText('Error')
        print 'Error in script: ', self.experimentPath[-1], ' - ', e