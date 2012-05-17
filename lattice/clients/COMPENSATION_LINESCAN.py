import sys, os
from PyQt4 import QtGui, QtCore,uic
from twisted.internet.defer import inlineCallbacks

SIGNALID = 21345

class uiContainerWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(uiContainerWidget,self).__init__(parent)
        basepath =  os.path.dirname(__file__)
        path = os.path.join(basepath,"qtui", "compensationlinescan.ui")
        uic.loadUi(path,self)

class COMPENSATION_LINESCAN_CONTROL(uiContainerWidget):
    def __init__(self, reactor,parent=None):
        super(COMPENSATION_LINESCAN_CONTROL,self).__init__(parent)
        self.reactor = reactor
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync()
        try:
            self.server = yield self.cxn.compensation_linescan
        except Exception:
            self.setEnabled(False)
            return
        yield self.setupListeners()
        angle = yield self.server.get_angle()
        amplitude = yield self.server.get_amplitude()
        angleRange = yield self.server.get_angle_range()
        amplitudeRange = yield self.server.get_amplitude_range()
        self.angle.setRange(*angleRange)
        self.amplitude.setRange(*amplitudeRange)
        self.angle.setValue(angle)
        self.amplitude.setValue(amplitude)
        #connect functions
        self.amplitude.valueChanged.connect(self.newAmplitude)
        self.angle.valueChanged.connect(self.newAngle)
        
    @inlineCallbacks
    def setupListeners(self):
        yield self.server.signal__new_range(SIGNALID)
        yield self.server.addListener(listener = self.followSignal, source = None, ID = SIGNALID)
    
    def followSignal(self, x, range):
        self.amplitude.setRange(*range)    
    
    @inlineCallbacks
    def newAmplitude(self, x):
        yield self.server.set_amplitude(x)
    
    @inlineCallbacks
    def newAngle(self, x):
        yield self.server.set_angle(x)
    
    def closeEvent(self, x):
        self.reactor.stop()
    
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    COMPENSATION_LINESCAN_CONTROL = COMPENSATION_LINESCAN_CONTROL(reactor)
    COMPENSATION_LINESCAN_CONTROL.show()
    reactor.run()