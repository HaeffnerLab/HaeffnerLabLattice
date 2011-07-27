from PyQt4 import QtGui, QtCore, uic
import os
import RGBconverter as RGB
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.error import ConnectError
from labrad.wrappers import connectAsync

SIGNALID1 = 187567
SIGNALID2 = 187568
SIGNALID3 = 187569
SIGNALID4 = 187570

class widgetWrapper():
    def __init__(self, chanName, wavelength, hint):
        self.chanName = chanName
        self.wavelength = wavelength
        self.hint = hint
        self.widget = None
        self.codeDict = codeDict = {-3.0: 'UnderExposed', -4.0: 'OverExposed', -5.0: 'NeedStartWM', -6.0 :'NotMeasured'}
        
        def makeWidget(self):
            self.widget = multiplexerChannel(self.wavelength, self.hint)
        
        def setFreq(self, freq):
            if freq in self.codeDict.keys():
                text = self.codeDict[freq]
            else:
                text = '%.5f'%freq
            self.widget.freq.setText(text)            
            
        def setState(self, state):
            self.widget.checkBox.setChecked(state)
        
        def setExposure(self, exposure):
            self.widget.spinBox.setValue(exposure)
            
class multiplexerWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/Multiplexer.ui')
        uic.loadUi(path,self)
        self.createDict()
        self.connect() 
    
    def createDict(self):
        self.d = {}
        self.d['397'] = widgetWrapper(chanName = '397',wavelength = '397', hint = '377.61131')
        self.d['866'] = widgetWrapper(chanName = '866',wavelength = '866', hint = '346.00002')
        self.d['422'] = widgetWrapper(chanName = '422',wavelength = '422', hint = '354.53921') 
        self.d['732'] = widgetWrapper(chanName = '732',wavelength = '732', hint = '409.09585') 
    
    @inlineCallbacks
    def connect(self):
        self.cxn = yield connectAsync()
        self.server = yield self.cxn.multiplexer_server
        yield self.initializeGUI()
        yield self.setupListeners()
        
    @inlineCallbacks
    def initializeGUI(self):
        #make sure channel names we have are found on the server
        availableNames = yield self.server.getAvailableChannels()
        for chanName in self.d.keys():
            if chanName not in availableNames:
                raise('Error chanName not found on the multiplexer server')
        #get initial values
        self.pushButton.setChecked(yield self.server.is_cycling())
        self.setButtonText()
        for widget in self.d.keys()
            freq = yield self.server.getFreq(name)
            self.d[name].setFreq(float(freq))
            exp = yield self.server.getExposure(name)
            self.d[name].setExposure(exp)
            state = yield self.server.getStaet(name)
            self.d[name].setState(state)
        #add items to grid layout
        self.grid.addWidget(self.d['397'],0,0)
        self.grid.addWidget(self.d['866'],1,0)
        self.grid.addWidget(self.d['422'],0,1)
        self.grid.addWidget(self.d['732'],1,1)
        #connect functions
        self.pushButton.toggled.connect(self.setOnOff)
        for widgetWrapper in self.d.values():
            widget = widgetWrapper.wdiget
            name = widgetWrapper.chanName
            widget.checkBox.valueChanged.connect(self.setStateWrapper(name))
            widget.spinBox.valueChanged.connect(self.setExposureWrapper(name))
    
    @inlineCallbacks
    def setupListeners(self):
        yield self.server.signal__channel_toggled(SIGNALID1)
        yield self.server.addListener(listener = self.followNewState, source = None, ID = SIGNALID1)
        yield self.server.signal__channel_new_exposure_set(SIGNALID2)
        yield self.server.addListener(listener = self.followNewExposure, source = None, ID = SIGNALID2)
        yield self.server.signal__channel_new_frequency(SIGNALID3)
        yield self.server.addListener(listener = self.followNewFreq, source = None, ID = SIGNALID3)
        yield self.server.signal__channel_now_cyclinng(SIGNALID4)
        yield self.server.addListener(listener = self.followNewCycling, source = None, ID = SIGNALID4)
    
    def followNewState(self,x,[chanName,state]):
        self.d[chanName].setState(state)
        
    def followNewExposure(self, x, [chanName,exp]):
        self.d[chanNAme].setExposure(exp)
    
    def followNewFreq(self, x, [chanName, freq]):
        self.d[chanName].setFreq(freq)
    
    def followNewCycling(self, x, cycling):
        self.setOnOff(cycling)
    
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
        
    def setStateWrapper(self, chanName):
        def func(self, state):
            self.setState(chanName, state)
        return func
    
    def setExposureWrapper(self, chanName):
        def func(self, state):
            self.setExposure(chanName, state)
        return func 
    
    @inlineCallbakcs
    def setState(self, chanName, state):
        yield self.server.setState(chanName,state)
    
    @inlineCallbacks
    def setExposure(self, chanName, exp):
        yield self.server.setExposure(chanName,exp)
                
class multiplexerChannel(QtGui.QWidget):
    def __init__(self, wavelength, hint, parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/MultiplexerChannel.ui')
        uic.loadUi(path,self)
        self.RGBconverter = RGB.RGBconverter()
        self.setColor(wavelength)
        self.setHint(hint)
        
    def setColor(self, wavelength):
        [r,g,b] = self.RGBconverter.wav2RGB(int(wavelength))
        self.label.setStyleSheet('color:rgb(%d,%d,%d)' %(r,g,b))
        self.label.setText(wavelength + 'nm')
    
    def setHint(self, hint):
        self.expectedfreq.setText(hint)