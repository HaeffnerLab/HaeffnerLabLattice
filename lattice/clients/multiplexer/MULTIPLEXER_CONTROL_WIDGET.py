from PyQt4 import QtGui, QtCore, uic
import os
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.error import ConnectError
from labrad.wrappers import connectAsync
import multiplexerchannel as mchan

class MULTIPLEXER_CONTROL_WIDGET(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/Multiplexer.ui')
        uic.loadUi(path,self)
        self.connect() 
    
    @inlineCallbacks
    def connect(self):
        self.cxn = yield connectAsync()
        self.server = yield self.cxn.multiplexer_server
        yield self.initializeGUI()
        
    @inlineCallbacks
    def initializeGUI(self):
        #get initial values
        self.pushButton.setChecked((yield self.server.is_cycling()))
        self.setButtonText()
        #connect functions
        self.pushButton.toggled.connect(self.setOnOff)
        #add items to grid layout
        self.chanwidgets = [mchan.Multiplexer_Channel(self.server,wl) for wl in ['397','866','422','732']]
        hints = ['377.61128','346.00002','354.53917','409.09585']
        for index,widget in enumerate(self.chanwidgets): widget.setText(hints[index])
        self.grid.addWidget(self.chanwidgets[0],0,0)
        self.grid.addWidget(self.chanwidgets[1],1,0)
        self.grid.addWidget(self.chanwidgets[2],0,1)
        self.grid.addWidget(self.chanwidgets[3],1,1)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateFreqs)
        self.timer.start(100)
        
    def setButtonText(self):
        if self.pushButton.isChecked():
            self.pushButton.setText('ON')
        else:
            self.pushButton.setText('OFF')
    
    @inlineCallbacks
    def setOnOff(self, pressed):
        if pressed:
            yield self.server.start_cycling()
        else:
            yield self.server.stop_cycling()
        self.setButtonText()
    
    @inlineCallbacks
    def updateFreqs(self):
        if self.pushButton.isChecked():
            freqs = yield self.server.get_frequencies()
            for chan in self.chanwidgets:
                chan.setFreq(freqs)