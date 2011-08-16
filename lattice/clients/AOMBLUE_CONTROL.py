import sys
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
from qtui.QCustomFreqPower import QCustomFreqPower

MinPower = -145 #dbM
MaxPower = 23
MinFreq = 70 #Mhz
MaxFreq = 90
UpdateTime = 100 #in ms, how often data is checked for communication with the server

class AOMBLUE_CONTROL(QCustomFreqPower):
    def __init__(self, server,parent=None):
        QCustomFreqPower.__init__( self, '397 Double Pass with red AO', parent )
        self.setPowerRange((MinPower,MaxPower))
        self.setFreqRange((MinFreq,MaxFreq))
        self.server= server
        #connect functions
        self.spinPower.valueChanged.connect(self.powerChanged)
        self.spinFreq.valueChanged.connect(self.freqChanged) 
        self.buttonSwitch.toggled.connect(self.switchChanged)
        #set initial values
        initpower = server.GetPower()
        initfreq = float(server.GetFreq())
        initstate = server.GetState()
        self.spinPower.setValue(initpower)
        self.spinFreq.setValue(initfreq)
        self.buttonSwitch.setChecked(initstate)
        self.setText(initstate)
        #keeping track of what's been updated
        self.powerUpdated = False;
        self.freqUpdated = False;
        self.switchUpdated = False;
        #start timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
        
    def powerChanged(self):
        self.powerUpdated = True;
	
    def freqChanged(self):
        self.freqUpdated = True;
	
    def switchChanged(self):
      self.switchUpdated = True
        	            
    #if inputs are updated by user, send updated values to server
    def sendToServer(self):
        if(self.powerUpdated):
            print '866 Double Pass sending new power'
            self.server.SetPower(self.spinPower.value())
            self.powerUpdated = False
        if(self.freqUpdated):
            print '866 Double Pass sending new frequency'
            self.server.SetFreq(self.spinFreq.value())
            self.freqUpdated = False
        if(self.switchUpdated):
            print '866 Double Pass sending new button'
            self.server.SetState(int(self.buttonSwitch.isChecked()))
            self.switchUpdated = False

if __name__=="__main__":
    import labrad
    cxn = labrad.connect()
    server = cxn.lattice_pc_rs_server_blue
    app = QtGui.QApplication(sys.argv)
    icon = AOMBLUE_CONTROL(server)
    icon.show()
    app.exec_()