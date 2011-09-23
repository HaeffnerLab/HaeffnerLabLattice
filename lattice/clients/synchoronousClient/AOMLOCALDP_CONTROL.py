import sys
from PyQt4 import QtGui
from QCustomFreqPower import QCustomFreqPower

MinPower = -145 #dbM
MaxPower = 24
MinFreq = 190 #Mhz
MaxFreq = 250

class RF_CONTROL(QCustomFreqPower):
    def __init__(self, server, name, parent=None):
        QCustomFreqPower.__init__( self, name,  parent )
        self.setPowerRange((MinPower,MaxPower))
        self.setFreqRange((MinFreq,MaxFreq))
        self.server= server
        #connect functions
        self.spinPower.valueChanged.connect(self.powerChanged)
        self.spinFreq.valueChanged.connect(self.freqChanged) 
        self.buttonSwitch.toggled.connect(self.switchChanged)
        #set initial values
        initpower = server.amplitude()
        initfreq = float(server.frequency())
        initstate = server.output()
        self.spinPower.setValue(initpower)
        self.spinFreq.setValue(initfreq)
        self.buttonSwitch.setChecked(initstate)
        self.setText(initstate)

    def powerChanged(self):
        self.server.amplitude(self.spinPower.value())
        
    def freqChanged(self):
        self.server.frequency(self.spinFreq.value())
    
    def switchChanged(self):
        self.server.output(self.buttonSwitch.isChecked())
        
if __name__=="__main__":
    import labrad
    cxn = labrad.connect()
    server = cxn.rohdeschwarz_server
    server.select_device('lattice-pc GPIB Bus - USB0::0x0AAD::0x0054::104543')
    app = QtGui.QApplication(sys.argv)
    icon = RF_CONTROL(server, name = 'Local Probe Double Pass')
    icon.show()
    app.exec_()