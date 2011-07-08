import sys
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad
import os
from labrad.types import Error
from qtui.QCustomSliderSpin import QCustomSliderSpin

UpdateTime = 100 #in ms, how often data is checked for communication with the server

class INTENSITY_CONTROL(QtGui.QWidget):
    def __init__(self, cxn ,parent=None):
        QtGui.QWidget.__init__(self, parent)
        #get initial information from servers
        self.server = cxn.dc_box
        self.registry = cxn.registry
        [Min397Intensity,Max397Intensity] = self.getRangefromReg()
        self.widg397 = QCustomSliderSpin('397 Intensity','mV',(Min397Intensity,Max397Intensity),(0,2500))
        self.widg397.spin.setValue(self.server.getIntensity397())
        #lay out the widget
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.widg397)
        #connect functions
        self.widg397.spin.valueChanged.connect(self.on397Update)
        self.widg397.minrange.valueChanged.connect(self.saveNewRange)
        self.widg397.maxrange.valueChanged.connect(self.saveNewRange)
        #start timer
        self.updated397 = False;
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
    
    def saveNewRange(self):
        [min397,max397] = [self.widg397.minrange.value(), self.widg397.maxrange.value()]
        self.registry.cd(['','Clients','Intensity Control'],True)
        self.registry.set('range397', [min397,max397])
         
    def on397Update(self):
        self.updated397 = True
    
    def getRangefromReg(self):
        self.registry.cd(['','Clients','Intensity Control'],True)
        try:
            [min397,max397] = self.registry.get('range397')
        except Error, e:
            if e.code is 21:
                [min397,max397] = [0,2500] #default min and max levels
        return [min397,max397]
	
	#if inputs are updated by user, send the values to server
    def sendToServer(self):
        if(self.updated397):
            print 'INTENSITY_CONTROL sending data'
            self.server.setIntensity397(self.widg397.spin.value())
            self.updated397 = False

if __name__=="__main__":
    cxn = labrad.connect()
    app = QtGui.QApplication(sys.argv)
    icon = INTENSITY_CONTROL(cxn)
    icon.show()
    app.exec_()