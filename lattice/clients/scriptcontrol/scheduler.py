from PyQt4 import QtGui, QtCore
from twisted.internet.task import LoopingCall

class Scheduler(QtGui.QTableWidget):
    def __init__(self, parent):
        QtGui.QTableWidget.__init__(self)
        self.parent = parent
        self.experimentRowDict = {}
        self.experimentTimerDict = {}
        self.checkBoxExperimentDict = {}
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
            self.experimentTimerDict[experiment].stop()

    def startExperiment(self, experiment):
        # start the experiment
        # we'll put in something to skip the first interval later
        self.parent.startExperiment(experiment)
        
        