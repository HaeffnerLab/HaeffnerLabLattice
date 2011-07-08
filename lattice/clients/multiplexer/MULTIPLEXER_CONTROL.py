import sys
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
import os
import multiplexerchannel as mchan

UpdateTime = 100#ms

class MULTIPLEXER_CONTROL(QtGui.QWidget):
    def __init__(self, server, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/Multiplexer.ui')
        uic.loadUi(path,self)
        self.server= server
        #set initial values
        self.pushButton.setChecked(self.server.is_cycling())
        self.setButtonText()
        #connect functions
        self.connect(self.pushButton, QtCore.SIGNAL('toggled(bool)'), self.setOnOff)
        #add items to grid layout
        self.chanwidgets = [mchan.Multiplexer_Channel(server,wl) for wl in ['397','866','422','732']]
        hints = ['377.61128','346.00002','354.53917','409.09585']
        for index,widget in enumerate(self.chanwidgets): widget.setText(hints[index])
        self.grid.addWidget(self.chanwidgets[0],0,0)
        self.grid.addWidget(self.chanwidgets[1],1,0)
        self.grid.addWidget(self.chanwidgets[2],0,1)
        self.grid.addWidget(self.chanwidgets[3],1,1)
        #create timer
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer,QtCore.SIGNAL("timeout()"),self.updateFreqs)
        self.timer.start(UpdateTime)
       
    def setOnOff(self, pressed):
        if pressed:
            self.server.start_cycling()
        else:
            self.server.stop_cycling()
        self.setButtonText()
            
    def setButtonText(self):
        if self.pushButton.isChecked():
            self.pushButton.setText('ON')
        else:
            self.pushButton.setText('OFF')
    
    def updateFreqs(self):
        if self.pushButton.isChecked():
            freqs = self.server.get_frequencies()
            for chan in self.chanwidgets:
                chan.setFreq(freqs)

if __name__=="__main__":
    import labrad
    cxn = labrad.connect()
    server = cxn.multiplexer_server
    app = QtGui.QApplication(sys.argv)
    icon = MULTIPLEXER_CONTROL(server)
    icon.show()
    app.exec_()