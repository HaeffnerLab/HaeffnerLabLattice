import sys
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad
from qtui.QCustomFreqPower import QCustomFreqPower

MinPower = -36 #dbM
MaxPower = 0
MinFreq = 0 #Mhz
MaxFreq = 20
UpdateTime = 100 #in ms, how often data is checked for communication with the server

class TRAPDRIVE_MODULATION_CONTROL(QCustomFreqPower):
    def __init__(self,server, parent=None):
        QCustomFreqPower.__init__( self, 'Trap Drive Modulation', (MinFreq,MaxFreq), (MinPower,MaxPower), parent )
        self.server = server
        #set initial values
        initpower = server.GetPower()
        initfreq = float(server.GetFreq())
        initstate = server.GetState()
        #set properties
        self.spinFreq.setDecimals(5)
        self.spinFreq.setSingleStep(10**-4) #set step size to 100HZ
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

    def switchChanged(self):
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

if __name__=='__main__':
    cxn = labrad.connect()
    server = cxn.lattice_pc_agilent_33220a_server
    app = QtGui.QApplication(sys.argv)
    icon = TRAPDRIVE_MODULATION_CONTROL(server)
    icon.show()
    app.exec_()