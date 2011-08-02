from qtui.QCustomFreqPower import QCustomFreqPower
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
from labrad.wrappers import connectAsync

class TRAPDRIVE_CONTROL(QtGui.QWidget):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        self.cxn = yield connectAsync()
        self.server = self.cxn.lattice_pc_hp_server
        self.widget = QCustomFreqPower('Trap Drive')
        self.setupWidget()
        
    @inlineCallbacks
    def setupWidget(self):
        #get ranges
        MinPower,MaxPower = yield self.server.get_power_range()
        MinFreq,MaxFreq = yield self.server.get_frequency_range()
        self.widget.setPowerRange((MinPower,MaxPower))
        self.widget.setFreqRange((MinFreq,MaxFreq))
        #get initial values
        initpower = yield self.server.getpower()
        initfreq = yield self.server.getfreq()
        initstate = yield self.server.getstate()
        self.widget.spinPower.setValue(initpower)
        self.widget.spinFreq.setValue(initfreq)
        self.widget.buttonSwitch.setChecked(initstate)
        self.widget.setText(initstate)
        #connect functions
        self.widget.spinPower.valueChanged.connect(self.powerChanged)
        self.widget.spinFreq.valueChanged.connect(self.freqChanged) 
        self.widget.buttonSwitch.toggled.connect(self.switchChanged)
        #add to layout
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.widget)
        
    @inlineCallbacks
    def powerChanged(self, pwr):
        yield self.server.setpower(pwr)
        
    @inlineCallbacks
    def freqChanged(self, freq):
        yield self.server.setfreq(freq)
        
    @inlineCallbacks
    def switchChanged(self, pressed):
        if pressed:
            yield self.server.setstate(pressed)
        else:
            self.dlg = MyAppDialog()
            self.dlg.accepted.connect(self.userAccept)
            self.dlg.rejected.connect(self.userReject)
            self.dlg.show()
    
    @inlineCallbacks 
    def userAccept(self):
        yield self.server.setstate(False)
        
    def userReject(self):
        self.widget.buttonSwitch.toggle()        
    
class MyAppDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.confirmButton = QtGui.QPushButton(Dialog)
        self.confirmButton.setText('Confirm')
        self.gridLayout.addWidget(self.confirmButton,1,0)
        self.declineButton = QtGui.QPushButton(Dialog)
        self.declineButton.setText('Decline')
        self.gridLayout.addWidget(self.declineButton,1,1)
        self.label = QtGui.QLabel('Turning off RF')
        self.font = QtGui.QFont()
        self.font.setPointSize(20)
        self.label.setFont(self.font)
        self.gridLayout.addWidget(self.label,0,0)
        self.confirmButton.clicked.connect(Dialog.accept)
        self.declineButton.clicked.connect(Dialog.reject)