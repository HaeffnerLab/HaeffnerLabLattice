from PyQt4 import QtGui, QtCore
from twisted.internet.task import LoopingCall
from twisted.internet.defer import inlineCallbacks

class Scheduler(QtGui.QTableWidget):
    def __init__(self, parent):
        QtGui.QTableWidget.__init__(self)
        self.parent = parent
        self.experimentRowDict = {}
        self.experimentTimerDict = {}
        self.checkBoxExperimentDict = {}
        self.experimentCounter = {} # tracks number of times an experiment has been called
        self.setupScheduler()
        
    def setupScheduler(self):
        self.setColumnCount(4)
        self.setRowCount(len(self.parent.experiments.keys()) + 1)
        
        experiments = self.parent.experiments.keys()
        experiments.sort()
        
        font = QtGui.QFont('MS Shell Dlg 2',pointSize=10)
        font.setUnderline(True)        
        item = QtGui.QTableWidgetItem('Experiment')
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        item.setFont(font)
        self.setItem(0, 0, item)
        item = QtGui.QTableWidgetItem('Start Upon Enable')
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        item.setFont(font)
        self.setItem(0, 1, item)        
        item = QtGui.QTableWidgetItem('Interval (s)')
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        item.setFont(font)        
        self.setItem(0, 2, item)
        item = QtGui.QTableWidgetItem('Enable')
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        item.setFont(font)        
        self.setItem(0, 3, item)
                    
        row = 1
        for experiment in experiments:
            self.experimentCounter[experiment] = 0
            self.experimentRowDict[experiment] = row
            experimentLabel = QtGui.QLabel(experiment[-1])
            self.setCellWidget(row, 0, experimentLabel)
            startNowCheckBox = QtGui.QCheckBox()
            self.setCellWidget(row, 1, startNowCheckBox)
            intervalDoubleSpinBox = QtGui.QDoubleSpinBox()
            intervalDoubleSpinBox.setRange(0, 1000000)
            intervalDoubleSpinBox.setDecimals(2)
            intervalDoubleSpinBox.setValue(30)
            intervalDoubleSpinBox.setKeyboardTracking(False)
            self.setCellWidget(row, 2, intervalDoubleSpinBox)
            enableCheckBox = QtGui.QCheckBox()
            self.setCellWidget(row, 3, enableCheckBox)
            self.checkBoxExperimentDict[enableCheckBox] = experiment 
            enableCheckBox.stateChanged.connect(self.checkBoxStateChangedSignal)            
            row += 1

        self.resizeColumnsToContents()  
        self.horizontalHeader().setStretchLastSection(True)
            
    def checkBoxStateChangedSignal(self, evt):
        experiment = self.checkBoxExperimentDict[self.sender()]
        if (bool(evt) == True):
            self.experimentTimerDict[experiment] = LoopingCall(self.startExperiment, experiment)
            self.experimentTimerDict[experiment].start(self.cellWidget(self.experimentRowDict[experiment], 2).value())
        else:
            # stop
            self.experimentCounter[experiment] = 0
            self.experimentTimerDict[experiment].stop()

    @inlineCallbacks
    def startExperiment(self, experiment):
        # start the experiment
        # we'll put in something to skip the first interval later
        if (self.experimentCounter[experiment] == 0 and (self.cellWidget(self.experimentRowDict[experiment], 1).isChecked() == False)):
            pass
        else:
#            status = yield self.parent.cxn.semaphore.get_parameter(list(experiment) + ['Semaphore', 'Status'], context = self.parent.statusContext)
            if (experiment == tuple(self.parent.statusWidget.experimentPath)):
                yield self.parent.statusWidget.startButtonSignal(1)
            else:
                yield self.parent.cxn.semaphore.set_parameter(list(experiment) + ['Semaphore', 'Continue'], True, context = self.parent.statusContext)
                yield self.parent.cxn.semaphore.set_parameter(list(experiment) + ['Semaphore', 'Block'], False, context = self.parent.statusContext)
                yield self.parent.cxn.semaphore.set_parameter(list(experiment) + ['Semaphore', 'Status'], 'Running', context = self.parent.statusContext)                      
                self.parent.startExperiment(experiment)
        self.experimentCounter[experiment] += 1
        
        