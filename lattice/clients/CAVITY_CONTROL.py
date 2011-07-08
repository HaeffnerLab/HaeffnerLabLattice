import sys
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad
import os
from labrad.types import Error
from qtui.QCustomSliderSpin import QCustomSliderSpin

UpdateTime = 100 #in ms, how often data is checked for communication with the server
GlobalRange = (0,2500)
class CAVITY_CONTROL(QtGui.QWidget):
    def __init__(self, cxn ,parent=None):
        QtGui.QWidget.__init__(self, parent)
        #get initial information from servers
        self.server = cxn.laserdac
        self.registry = cxn.registry
        [MinLevel397,MaxLevel397, MinLevel866,MaxLevel866, MinLevel422, MaxLevel422] = self.getRangefromReg()
        val397 = self.server.getCavity('397')
        val866 = self.server.getCavity('866')
        val422 = self.server.getCavity('422')      
        #lay out the widget
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.widg397 = QCustomSliderSpin('397 Cavity','mV',(MinLevel397,MaxLevel397),GlobalRange)
        self.widg866 = QCustomSliderSpin('866 Cavity','mV',(MinLevel866,MaxLevel866),GlobalRange)
        self.widg422 = QCustomSliderSpin('422 Offset','mV',(MinLevel422,MaxLevel422),GlobalRange)
        self.widg397.spin.setValue(val397)
        self.widg866.spin.setValue(val866)
        self.widg422.spin.setValue(val422)
        layout.addWidget(self.widg397)
        layout.addWidget(self.widg866)
        layout.addWidget(self.widg422)
        #connect functions
        self.widg397.spin.valueChanged.connect(self.on397Update)
        self.widg866.spin.valueChanged.connect(self.on866Update)
        self.widg422.spin.valueChanged.connect(self.on422Update)
        self.widg397.minrange.valueChanged.connect(self.saveNewRange)
        self.widg397.maxrange.valueChanged.connect(self.saveNewRange)
        self.widg866.minrange.valueChanged.connect(self.saveNewRange)
        self.widg866.maxrange.valueChanged.connect(self.saveNewRange)
        self.widg422.minrange.valueChanged.connect(self.saveNewRange)
        self.widg422.maxrange.valueChanged.connect(self.saveNewRange)
        #start timer
        self.updated397 = False
        self.updated866 = False
        self.updated422 = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
    
    def saveNewRange(self):
        [min397,max397] = [self.widg397.minrange.value(), self.widg397.maxrange.value()]
        [min866,max866] = [self.widg866.minrange.value(), self.widg866.maxrange.value()]
        [min422,max422] = [self.widg422.minrange.value(), self.widg422.maxrange.value()]
        self.registry.cd(['','Clients','Cavity Control'],True)
        self.registry.set('range397', [min397,max397])
        self.registry.set('range866', [min866,max866])
        self.registry.set('range422', [min422,max422])
        
    def on397Update(self):
        self.updated397 = True
    
    def on866Update(self):
        self.updated866 = True
    
    def on422Update(self):
        self.updated422 = True
    
    def getRangefromReg(self):
        self.registry.cd(['','Clients','Cavity Control'],True)
        try:
            [min397,max397] = self.registry.get('range397')
            [min866,max866] = self.registry.get('range866')
            [min422,max422] = self.registry.get('range422')
        except Error, e:
            if e.code is 21:
                [min397,max397] = [0,2500] #default min and max levels
                [min866,max866] = [0,2500]
                [min422,max422] = [0,2500]
        return [min397,max397,min866,max866, min422,max422]
	
	#if inputs are updated by user, send the values to server
    def sendToServer(self):
        if(self.updated397):
            print 'CAVITY_CONTROL sending data'
            self.server.setCavity('397',self.widg397.spin.value())
            self.updated397 = False
        if(self.updated866):
            print 'CAVITY_CONTROL sending data'
            self.server.setCavity('866',self.widg866.spin.value())
            self.updated866 = False
        if(self.updated422):
            print 'CAVITY_CONTROL sending data'
            self.server.setCavity('866',self.widg866.spin.value())
            self.updated422 = False
  
if __name__=="__main__":
    cxn = labrad.connect()
    app = QtGui.QApplication(sys.argv)
    icon = CAVITY_CONTROL(cxn)
    icon.show()
    app.exec_()