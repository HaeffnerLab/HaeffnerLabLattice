from PyQt4 import QtGui, QtCore, uic
import os
import RGBconverter as RGB
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.error import ConnectError
from labrad.wrappers import connectAsync

class multiplexerWidget(QtGui.QWidget):
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
                
class multiplexerChannel(QtGui.QWidget):
    def __init__(self, server, wavelength, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/MultiplexerChannel.ui')
        uic.loadUi(path,self)
        self.server = server
        self.RGBconverter = RGB.RGBconverter()
        self.wavelength = wavelength
        self.initializeValues()
        
    @inlineCallbacks
    def initializeValues(self):
        self.channel = yield self.server.get_channel_from_wavelength(self.wavelength)
        #set initial values
        [r,g,b] = self.RGBconverter.wav2RGB(int(self.wavelength))
        self.label.setStyleSheet('color:rgb(%d,%d,%d)' %(r,g,b))
        self.label.setText(self.wavelength + 'nm')
        isSelected = self.channel in (yield self.server.get_selected_channels())
        self.checkBox.setChecked(isSelected)
        exposure = (yield self.server.get_exposures())[self.channel]
        self.spinBox.setValue(exposure)
        #connect functions
        self.connect(self.checkBox, QtCore.SIGNAL('stateChanged(int)'), self.measureChannel)
        self.connect(self.spinBox, QtCore.SIGNAL('valueChanged(int)'), self.setExposure)
        
    def measureChannel(self, state):
        self.server.toggle_channel(self.channel, self.checkBox.isChecked())

    def setExposure(self, exp):
        self.server.set_exposure(self.channel,exp)
    
    def setText(self, text):
        self.expectedfreq.setText(text)
        
    def setFreq(self,freqlist):
        if self.checkBox.isChecked():
            freq = freqlist[self.channel]
            if freq is not None:
                if float(freq) == -3.0:
                    text = 'UnderExposed'
                elif float(freq) == -4.0:
                    text = 'OverExposed'
                elif float(freq) == -5.0:
                    text = 'NeedStartWM'
                else:
                    text =  '%.5f'%freq
            else:
                text = 'NotMeasured'
        else:
            text = 'NotMeasured'
        self.freq.setText(text)