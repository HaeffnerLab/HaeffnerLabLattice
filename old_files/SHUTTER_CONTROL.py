import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad

UpdateTime = 100 #in ms, how often data is checked for communication with the server
MaxIntensity = 2500
MinIntensity = 0

class SHUTTER_CONTROL(QtGui.QWidget):
    def __init__(self, server, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/shutterfrontend.ui')
        uic.loadUi(path,self)
        self.server = server
        #set parameters
        self.intensity397Spin.setKeyboardTracking(False)
        self.minintensity397Spin.setKeyboardTracking(False)
        self.maxintensity397Spin.setKeyboardTracking(False)      
        self.intensity397Spin.setRange(MinIntensity,MaxIntensity)
        self.intensity397Slider.setRange(MinIntensity,MaxIntensity)
        self.minintensity397Spin.setRange(MinIntensity,MaxIntensity)
        self.maxintensity397Spin.setRange(MinIntensity,MaxIntensity)
    	#connect functions
        self.connect(self.shutterOne, QtCore.SIGNAL('toggled(bool)'), self.buttonOneToggled)
        self.connect(self.shutterTwo, QtCore.SIGNAL('toggled(bool)'), self.buttonTwoToggled)
    	self.connect(self.shutterThree, QtCore.SIGNAL('toggled(bool)'), self.buttonThreeToggled)
        self.connect(self.intensity397Spin, QtCore.SIGNAL('valueChanged(int)'),self.spin397Changed)
        self.connect(self.intensity397Slider, QtCore.SIGNAL('valueChanged(int)'),self.slider397Changed)
        self.connect(self.minintensity397Spin,QtCore.SIGNAL('valueChanged(int)'),self.rangeChanged)
        self.connect(self.maxintensity397Spin,QtCore.SIGNAL('valueChanged(int)'),self.rangeChanged)
        #set initialvalues
        self.buttonsUpdated=[0,0,0]
        self.intensityUpdated = False
        self.shutterOne.setChecked(server.getShutter(1))
        self.shutterTwo.setChecked(server.getShutter(2))
        self.shutterThree.setChecked(server.getShutter(3))
        self.intensity397Spin.setValue(server.getIntensity397())
        self.intensity397Slider.setValue(server.getIntensity397())
        self.setButtonText(self.shutterOne, 'Shutter 1')
        self.setButtonText(self.shutterTwo, 'Shutter 2')
        self.setButtonText(self.shutterThree, 'PB Trigger')
        #start timer
        self.buttonsUpdated=[0,0,0]
        self.intensityUpdated = False
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer,QtCore.SIGNAL("timeout()"),self.sendToServer)
        self.timer.start(UpdateTime)
    
    def spin397Changed(self):
        self.intensity397Slider.setValue(self.intensity397Spin.value())
        self.intensityUpdated =True
    
    def slider397Changed(self):
        self.intensity397Spin.setValue(self.intensity397Slider.value())
        self.intensityUpdated =True
    
    def rangeChanged(self):
        min = self.minintensity397Spin.value()
        max = self.maxintensity397Spin.value()
        self.intensity397Slider.setRange(min,max)
    

    def buttonOneToggled(self, x):
        self.buttonsUpdated[0] = 1
        self.setButtonText(self.shutterOne, 'Shutter 1')
        
    def buttonTwoToggled(self, x):
        self.buttonsUpdated[1] = 1
        self.setButtonText(self.shutterTwo, 'Shutter 2')
        
    def buttonThreeToggled(self, x):
        self.buttonsUpdated[2] = 1
        self.setButtonText(self.shutterThree, 'PB Trigger')
    
    def setButtonText(self, button, prefix):
        if button.isChecked():
            button.setText(prefix + ' ON')
        else:
            button.setText(prefix + ' OFF')
    
    
#    #if inputs are updated by user, send the LCD values to server
    def sendToServer(self):
        if(self.buttonsUpdated[0]):
            self.buttonsUpdated[0] = 0
            self.server.setshutter(1,self.shutterOne.isChecked())
            print 'SHUTTER_CONTROL sending data'
        if(self.buttonsUpdated[1]):
            self.buttonsUpdated[1] = 0
            self.server.setshutter(2,self.shutterTwo.isChecked())
            print 'SHUTTER_CONTROL sending data'
        if(self.buttonsUpdated[2]):
            self.buttonsUpdated[2] = 0               
            self.server.setshutter(3,self.shutterThree.isChecked())
            print 'SHUTTER_CONTROL sending data'
        if(self.intensityUpdated):
            self.intensityUpdated = False
            self.server.setIntensity397(self.intensity397Spin.value())
            print 'SHUTTER CONTROL sending data'
            
            
if __name__=="__main__":
    cxn = labrad.connect()
    server = cxn.dc_box
    app = QtGui.QApplication(sys.argv)
    icon = SHUTTER_CONTROL(server)
    icon.show()
    app.exec_()

 
