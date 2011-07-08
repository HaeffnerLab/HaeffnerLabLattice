import sys
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad
from qtui.QCustomFreqPower import QCustomFreqPower

MinFreq = 15 #Mhz
MaxFreq = 17
UpdateTime = 100 #in ms, how often data is checked for communication with the server

class TRAPDRIVE_CONTROL(QCustomFreqPower):
    def __init__(self,server, parent=None):
        self.server = server
        MinPower,MaxPower = self.server.get_power_range()
        QCustomFreqPower.__init__( self, 'Trap Drive', (MinFreq,MaxFreq), (MinPower,MaxPower), parent )
        #set initial values
        initpower = server.GetPower()
        initfreq = float(server.GetFreq())
        initstate = server.GetState()
        self.spinPower.setValue(initpower)
        self.spinFreq.setValue(initfreq)
        self.buttonSwitch.setChecked(initstate)
        self.setText(initstate)
        #connect functions
        self.spinPower.valueChanged.connect(self.powerChanged)
        self.spinFreq.valueChanged.connect(self.freqChanged) 
        self.buttonSwitch.toggled.connect(self.switchChanged)
        #keeping track of what's been updated
        self.powerUpdated = False;
        self.freqUpdated = False;
        self.switchUpdated = False;
        #start timer
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer,QtCore.SIGNAL("timeout()"),self.sendToServer)
        self.timer.start(UpdateTime)
        
    def powerChanged(self):
        self.powerUpdated = True;
	
    def freqChanged(self):
        self.freqUpdated = True
	
    def userAccept(self):
        self.switchUpdated = True
        self.setText(False)
        
    def userReject(self):
        self.buttonSwitch.toggle()
        self.setText(True)
        
    def switchChanged(self, down):
        if not down:
            self.dlg = MyAppDialog()
            self.connect(self.dlg, QtCore.SIGNAL("accepted()"), self.userAccept)
            self.connect(self.dlg, QtCore.SIGNAL("rejected()"), self.userReject)
            self.dlg.show()
        else:
            self.switchUpdated = True
            
    
    #if inputs are updated by user, send updated values to server
    def sendToServer(self):
        if(self.powerUpdated):
            print 'RF_GEN_CONTRL_GUI sending new power'
            self.server.SetPower(self.spinPower.value())
            self.powerUpdated = False
        if(self.freqUpdated):
            print 'RF_GEN_CONTRL_GUI sending new frequency'
            self.server.SetFreq(self.spinFreq.value())
            self.freqUpdated = False
        if(self.switchUpdated):
            print 'RF_GEN_CONTRL_GUI sending new button'
            self.server.SetState(int(self.buttonSwitch.isChecked()))
            self.switchUpdated = False

class MyAppDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setText('Confirm')
        self.gridLayout.addWidget(self.pushButton,1,0)
        self.pushButton2 = QtGui.QPushButton(Dialog)
        self.pushButton2.setText('Decline')
        self.gridLayout.addWidget(self.pushButton2,1,1)
        self.label = QtGui.QLabel('Turning off RF')
        self.font = QtGui.QFont()
        self.font.setPointSize(20)
        self.label.setFont(self.font)
        self.gridLayout.addWidget(self.label,0,0)
        QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"), Dialog.accept)
        QtCore.QObject.connect(self.pushButton2,QtCore.SIGNAL("clicked()"), Dialog.reject)
    

if __name__=='__main__':
    cxn = labrad.connect()
    server = cxn.lattice_pc_hp_server
    app = QtGui.QApplication(sys.argv)
    icon = TRAPDRIVE_CONTROL(server)
    icon.show()
    app.exec_()