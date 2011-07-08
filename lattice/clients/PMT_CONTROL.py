import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import labrad
import time

REFRESHTIME = .5 #in sec how often PMT is updated


class PMT_CONTROL(QtGui.QWidget):
    def __init__(self, server, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/pmtfrontend.ui')
        uic.loadUi(path,self)
        self.server = server
        #connect functions
        self.pushButton.toggled.connect(self.on_toggled)
        self.thread = dataGetter(self.server, parent=self)
        self.thread.gotNewData.connect(self.onNewData)
        self.thread.finished.connect(lambda: self.thread.start() if self.pushButton.isChecked() else None)
        isreceiving = self.server.isreceiving()
        self.setText(self.pushButton)
        self.pushButton.setChecked(isreceiving)
        dataset = self.server.currentdataset()
        self.lineEdit.setText(dataset)
        duration = self.server.getcollectionperiod()
        self.doubleSpinBox.setValue(duration)
        self.doubleSpinBox.valueChanged.connect(self.onNewDuration)
        self.newSet.clicked.connect(self.onNewSet)
        
    def on_toggled(self, state):
        if state:
            self.server.startreceiving()
            self.thread.start()
        else:
            self.server.stopreceiving()
            self.lcdNumber.display(0)
        self.setText(self.pushButton)
        
    def onNewSet(self):
        newset = self.server.newdataset()
        self.lineEdit.setText(newset)
    
    def setText(self, obj):
        state = obj.isChecked()
        if state:
            obj.setText('ON')
        else:
            obj.setText('OFF')
    
    def onNewData(self,count):
        self.lcdNumber.display(count)
        
    def onNewDuration(self, value):
        self.server.setcollectionperiod(value)
        
            
class dataGetter(QtCore.QThread):
    gotNewData = QtCore.pyqtSignal(float)
    def __init__(self, server, parent=None,):
        QtCore.QThread.__init__(self,parent)
        self.server = server
    def run(self):
        count = self.server.getnextreadings(1)[0][1]
        self.gotNewData.emit(count)
        time.sleep(REFRESHTIME)
            
            
if __name__=="__main__":
    cxn = labrad.connect()
    server = cxn.pmt_server
    app = QtGui.QApplication(sys.argv)
    icon = PMT_CONTROL(server)
    icon.show()
    app.exec_()

 
