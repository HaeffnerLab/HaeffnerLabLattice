import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad

UpdateTime = 100 #in ms, how often data is checked for communication with the server

class SHUTTER_CONTROL(QtGui.QWidget):
    def __init__(self, server, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/shutterfrontend.ui')
        uic.loadUi(path,self)
        self.server = server
    	#connect functions
        self.shutterOne.toggled.connect(self.buttonOneToggled)
        self.shutterTwo.toggled.connect(self.buttonTwoToggled)
        self.shutterThree.toggled.connect(self.buttonThreeToggled)
        #set initial values
        self.buttonsUpdated=[0,0,0]
        self.shutterOne.setChecked(server.getShutter(1))
        self.shutterTwo.setChecked(server.getShutter(2))
        self.shutterThree.setChecked(server.getShutter(3))
        self.setButtonText(self.shutterOne, 'Blue PI')
        self.setButtonText(self.shutterTwo, 'Red PI')
        self.setButtonText(self.shutterThree, 'PB Trigger')
        #start timer
        self.buttonsUpdated=[0,0,0]
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
    
    def buttonOneToggled(self, x):
        self.buttonsUpdated[0] = 1
        self.setButtonText(self.shutterOne, 'Blue PI')
        
    def buttonTwoToggled(self, x):
        self.buttonsUpdated[1] = 1
        self.setButtonText(self.shutterTwo, 'Red PI')
        
    def buttonThreeToggled(self, x):
        self.buttonsUpdated[2] = 1
        self.setButtonText(self.shutterThree, 'PB Trigger')
    
    def setButtonText(self, button, prefix):
        if button.isChecked():
            button.setText(prefix + ' ON')
        else:
            button.setText(prefix + ' OFF')

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
            
if __name__=="__main__":
    cxn = labrad.connect()
    server = cxn.dc_box
    app = QtGui.QApplication(sys.argv)
    icon = SHUTTER_CONTROL(server)
    icon.show()
    app.exec_()