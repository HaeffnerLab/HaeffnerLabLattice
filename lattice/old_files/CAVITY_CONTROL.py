import sys
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad
import os
from labrad.types import Error

UpdateTime = 100 #in ms, how often data is checked for communication with the server

class CAVITY_CONTROL(QtGui.QWidget):
    def __init__(self, cxn ,parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/cavityfrontend.ui')
        uic.loadUi(path,self)
        self.server = cxn.laserdac
        self.registry = cxn.registry
        [MinLevel397,MaxLevel397, MinLevel866,MaxLevel866] = self.getRangefromReg()
        #set ranges for all widgets
        self.min397Spin.setRange(0,2500)
        self.max397Spin.setRange(0,2500)
        self.min866Spin.setRange(0,2500)
        self.max866Spin.setRange(0,2500)
        self.cavity397Spin.setRange(MinLevel397,MaxLevel397)
        self.cavity866Spin.setRange(MinLevel866,MaxLevel866)
        self.cavity397Slider.setRange(MinLevel397,MaxLevel397)
        self.cavity866Slider.setRange(MinLevel866,MaxLevel866)
        #set initial values for ranges
        self.min397Spin.setValue(MinLevel397)
        self.min866Spin.setValue(MinLevel866)
        self.max397Spin.setValue(MaxLevel397)
        self.max866Spin.setValue(MaxLevel866)
        #connect functions
        self.connect(self.cavity397Slider, QtCore.SIGNAL('valueChanged(int)'), self.slider397Changed)
        self.connect(self.cavity866Slider, QtCore.SIGNAL('valueChanged(int)'), self.slider866Changed)
        self.connect(self.cavity397Spin, QtCore.SIGNAL('valueChanged(int)'), self.spin397Changed)
        self.connect(self.cavity866Spin, QtCore.SIGNAL('valueChanged(int)'), self.spin866Changed)
        self.connect(self.min397Spin, QtCore.SIGNAL('valueChanged(int)'), self.limitsChanged)
        self.connect(self.max397Spin, QtCore.SIGNAL('valueChanged(int)'), self.limitsChanged)
        self.connect(self.min866Spin, QtCore.SIGNAL('valueChanged(int)'), self.limitsChanged)
        self.connect(self.max866Spin, QtCore.SIGNAL('valueChanged(int)'), self.limitsChanged)
        #turn off keyboard tracking on all spins
        self.cavity397Spin.setKeyboardTracking(False)
        self.cavity866Spin.setKeyboardTracking(False)
        self.min397Spin.setKeyboardTracking(False)
        self.max397Spin.setKeyboardTracking(False)
        self.min866Spin.setKeyboardTracking(False)
        self.max866Spin.setKeyboardTracking(False)
        #set initial values
        val397 = self.server.getCavity('397')
        val866 = self.server.getCavity('866')
        self.cavity397Slider.setValue(int(round(val397)))
        self.cavity866Slider.setValue(int(round(val866)))
        self.cavity866Spin.setValue(int(round(val397))) 
        self.cavity866Spin.setValue(int(round(val866)))
        #start timer
        self.updated397 = False;
        self.updated866 = False
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer,QtCore.SIGNAL("timeout()"),self.sendToServer)
        self.timer.start(UpdateTime)
    
    def getRangefromReg(self):
        self.registry.cd(['','Clients','Cavity Control'],True)
        try:
            [min397,max397] = self.registry.get('range397')
            [min866,max866] = self.registry.get('range866')
        except Error, e:
            if e.code is 21:
                [min397,max397] = [0,2500] #default min and max levels
                [min866,max866] = [0,2500]
        return [min397,max397,min866,max866]
        
    def limitsChanged(self):
        min397 = self.min397Spin.value()
        max397 = self.max397Spin.value()
        min866 = self.min866Spin.value()
        max866 = self.max866Spin.value()
        self.cavity397Spin.setRange(min397,max397)
        self.cavity397Slider.setRange(min397,max397)
        self.cavity866Spin.setRange(min866,max866)
        self.cavity866Slider.setRange(min866,max866)  
        self.registry.cd(['','Clients','Cavity Control'],True)
        self.registry.set('range397',[min397,max397])
        self.registry.set('range866',[min866,max866]) 
        
    def slider397Changed(self):
        self.cavity397Spin.setValue(self.cavity397Slider.value())
        self.updated397 = True;
		
    def slider866Changed(self):
        self.cavity866Spin.setValue(self.cavity866Slider.value())
        self.updated866 = True;
      
    def spin397Changed(self):
        self.cavity397Slider.setValue(self.cavity397Spin.value())
        self.updated397 = True;

    def spin866Changed(self):
        self.cavity866Slider.setValue(self.cavity866Spin.value())
        self.updated866 = True;
	
	
    #if inputs are updated by user, send the values to server
    def sendToServer(self):
        if(self.updated397):
            print 'CAVITY_CONTROL sending data'
            self.server.setCavity('397',self.cavity397Spin.value())
            self.updated397 = False
        if(self.updated866):
	    print 'CAVITY_CONTROL sending data'
            self.server.setCavity('866',self.cavity866Spin.value())
            self.updated866 = False
  
if __name__=="__main__":
    cxn = labrad.connect()
    app = QtGui.QApplication(sys.argv)
    icon = CAVITY_CONTROL(cxn)
    icon.show()
    app.exec_()