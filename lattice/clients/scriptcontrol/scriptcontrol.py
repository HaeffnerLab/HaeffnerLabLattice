import time
from twisted.internet.defer import inlineCallbacks, DeferredList
from twisted.internet.threads import deferToThread
from PyQt4 import QtGui, QtCore
import re
from experimentlist import ExperimentListWidget
from experimentgrid import ExperimentGrid
from globalgrid import GlobalGrid
from parameterlimitswindow import ParameterLimitsWindow
from status import StatusWidget

class ScriptControl(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        QtGui.QWidget.__init__(self)
        self.reactor = reactor
        
        # import all the experiments
        import experiments.Test
        import experiments.Test2
        import scripts.simpleMeasurements.ADCpowerMonitor
        import scripts.experiments.Experiments729.spectrum
        import scripts.experiments.Experiments729.rabi_flopping        
        # main dictionary organized by path in the Registry

        self.experiments = {
                            ('Test', 'Exp1'):  (experiments.Test, 'Test'),
                            ('Test', 'Exp2'):  (experiments.Test2, 'Test2'),
                            ('SimpleMeasurements', 'ADCPowerMonitor'):  (scripts.simpleMeasurements.ADCpowerMonitor, 'ADCPowerMonitor'),
                            ('729Experiments','Spectrum'):  (scripts.experiments.Experiments729.spectrum, 'spectrum'),
                            ('729Experiments','RabiFlopping'):  (scripts.experiments.Experiments729.rabi_flopping, 'rabi_flopping')
                           }
        self.setupExperimentProgressDict()
        self.connect()
        
    # A dictionary to keep track of the progress of each experiment
    def setupExperimentProgressDict(self):
        self.experimentProgressDict = self.experiments.copy()
        for key in self.experimentProgressDict.keys():
            self.experimentProgressDict[key] = 0.0
        
    # Connect to LabRAD
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync()
        self.server = self.cxn.semaphore
        self.setupMainWidget()
    
    # Setup the main layout
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
        
        # Labels
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
        
        # Setup Experiment List Widget
        self.experimentListWidget = ExperimentListWidget(self)
        self.experimentListWidget.show()
        self.mainGrid.addWidget(self.experimentListWidget, 1, 0, QtCore.Qt.AlignCenter)
        
        # Setup Experiment Parameter Widget
        yield deferToThread(time.sleep, .05) # necessary delay. Qt issue.
        self.setupExperimentGrid(['Test', 'Exp1']) # the experiment to start with
        parameterLimitsButton = QtGui.QPushButton("Parameter Limits", self)
        parameterLimitsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        parameterLimitsButton.clicked.connect(self.parameterLimitsWindowEvent)
        self.mainGrid.addWidget(parameterLimitsButton, 2, 1, QtCore.Qt.AlignCenter)
        # Setup Global Parameter Widget
        self.setupGlobalGrid(['Test', 'Exp1']) # the experiment to start with
        # Setup Status Widget
        self.setupStatusWidget(['Test', 'Exp1']) # the experiment to start with
        
        self.mainLayout.addLayout(self.mainGrid)
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
        
    # Returns a different widget depending on the type of value provided by the semaphore 
    def typeCheckerWidget(self, Value):
        # boolean
        if (type(Value) == bool):
            checkbox = QtGui.QCheckBox()
            if (Value == True):
                checkbox.toggle()
            return checkbox
        else:
            value = Value.aslist

        from labrad.units import Value as labradValue
        if ((type(value) == list) and (len(value) == 3) and (type(value[0]) == labradValue)):
            doubleSpinBox = QtGui.QDoubleSpinBox()
            doubleSpinBox.setRange(value[0], value[1])
            number_dec = len(str(value[0].value-int(value[0].value))[2:])
            doubleSpinBox.setDecimals(number_dec + 1)
            doubleSpinBox.setValue(value[2])
            doubleSpinBox.setSuffix(' ' + value[2].units)
            doubleSpinBox.setSingleStep(.1)
            doubleSpinBox.setKeyboardTracking(False)
            doubleSpinBox.setMouseTracking(False)
            return doubleSpinBox
        # list with more or less than 3 values
        else:
            lineEdit = QtGui.QLineEdit()       
            text = str(value)
            text = re.sub('Value', '', text)
            lineEdit.setText(text)
            return lineEdit
    
    @inlineCallbacks
    def startExperiment(self, experiment):
        reload(self.experiments[experiment][0])
        class_ = getattr(self.experiments[experiment][0], self.experiments[experiment][1])
        instance = class_()
        yield deferToThread(instance.run)
        
    def saveParametersToRegistry(self, res):
        return self.server.save_parameters_to_registry()
    
    def stopReactor(self, res):
        self.reactor.stop()
    
    def closeEvent(self, x):
        dl = [self.cxn.semaphore.set_parameter(list(experiment) + ['Semaphore', 'Status'], 'Stopped', context = self.statusContext) for experiment in self.experiments.keys()]
        dl = DeferredList(dl)
        dl.addCallback(self.saveParametersToRegistry)
        dl.addCallback(self.stopReactor)

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    scriptControl = ScriptControl(reactor)
    reactor.run()

