from PyQt4 import QtGui, QtCore, uic
from labrad.wrappers import connectAsync
from twisted.internet.defer import inlineCallbacks, returnValue
from labrad.types import Error
import os

SIGNALID = 874193

class pmtWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/pmtfrontend.ui')
        uic.loadUi(path,self)
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        cxn = yield connectAsync()
        self.server = cxn.normalpmtflow
        yield self.initializeContent()
        yield self.setupListeners()
        #connect functions
        self.pushButton.toggled.connect(self.on_toggled)
        self.newSet.clicked.connect(self.onNewSet)
        self.doubleSpinBox.valueChanged.connect(self.onNewDuration)
        self.comboBox.currentIndexChanged.connect(self.onNewMode)
    
    @inlineCallbacks
    def setupListeners(self):
        yield self.server.signal__new_count(SIGNALID)
        yield self.server.addListener(listener = self.followSignal, source = None, ID = SIGNALID)
    
    @inlineCallbacks
    def initializeContent(self):
        dataset = yield self.server.currentdataset()
        self.lineEdit.setText(dataset)
        running = yield self.server.isrunning()
        self.pushButton.setChecked(running)
        self.setText(self.pushButton)
        duration = yield self.server.get_time_length()
        self.doubleSpinBox.setValue(duration)
    
    def followSignal(self,signal,value):
        self.lcdNumber.display(value)
    
    @inlineCallbacks
    def on_toggled(self, state):
        if state:
            yield self.server.record_data()
            newset = yield self.server.currentdataset()
            self.lineEdit.setText(newset)
        else:
            yield self.server.stoprecording()
            self.lcdNumber.display(0)
        self.setText(self.pushButton)
    
    @inlineCallbacks
    def onNewSet(self, x):
        yield self.server.start_new_dataset()
        newset = yield self.server.currentdataset()
        self.lineEdit.setText(newset)
    
    @inlineCallbacks
    def onNewMode(self, mode):
        text = str(self.comboBox.itemText(mode))
        yield self.server.set_mode(text)
        
    def setText(self, obj):
        state = obj.isChecked()
        if state:
            obj.setText('ON')
        else:
            obj.setText('OFF')
    
    def onNewData(self,count):
        self.lcdNumber.display(count)
    
    @inlineCallbacks
    def onNewDuration(self, value):
        yield self.server.set_time_length(value)