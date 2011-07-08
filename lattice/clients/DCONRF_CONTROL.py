import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad

UpdateTime = 100 #in ms, how often data is checked for communication with the server

class DCONRF_CONTROL(QtGui.QWidget):
    def __init__(self, server, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/dconrf.ui')
        uic.loadUi(path,self)
        self.server = server
    	#connect functions
        self.doubleSpinBox.setValue( self.server.getdcoffsetrf() )
        self.justUpdated = False
        self.doubleSpinBox.valueChanged.connect(self.onNewValue)
        #start timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
    
    def onNewValue(self):
        self.justUpdated = True
    
    def sendToServer(self):
        if(self.justUpdated):
            self.server.setdcoffsetrf(self.doubleSpinBox.value())
            print 'DCONRF_CONTROL sending data'
            self.justUpdated = False
            
if __name__=="__main__":
    cxn = labrad.connect()
    server = cxn.dc_box
    app = QtGui.QApplication(sys.argv)
    icon = DCONRF_CONTROL(server)
    icon.show()
    app.exec_()