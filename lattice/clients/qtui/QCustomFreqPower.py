import sys
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import os

class QCustomFreqPower(QtGui.QWidget):
    def __init__(self, title, freqrange, powerrange, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/powerfreqspin.ui')
        uic.loadUi(path,self)
        self.title.setText(title)
	self.spinPower.setRange(*powerrange)
	self.spinFreq.setRange(*freqrange)
	self.buttonSwitch.clicked.connect(self.setText)
	
	
    def setText(self, down):
      if down:
	self.buttonSwitch.setText('ON')
      else:
	self.buttonSwitch.setText('OFF') 

if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QCustomFreqPower('Control',(0,220),(-10,10))
    icon.show()
    app.exec_()