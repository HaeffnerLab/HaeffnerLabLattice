from PyQt4 import QtGui
import numpy

class durationWdiget(QtGui.QWidget):
    def __init__(self, reactor, value = 1, init_range = (1,1000), parent=None):
        super(durationWdiget, self).__init__(parent)
        self.reactor = reactor
        self.value = value
        self.ran = init_range
        self.initializeGUI()
        
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        durationLabel = QtGui.QLabel('Excitation Time')
        bandwidthLabel =  QtGui.QLabel('Fourier Bandwidth')
        self.duration = duration = QtGui.QSpinBox()
        duration.setSuffix('\265s')
        duration.setKeyboardTracking(False)
        duration.setRange(*self.ran)
        duration.setValue(self.value)
        initband = self.conversion(self.value)
        self.bandwidth = bandwidth = QtGui.QDoubleSpinBox()
        bandwidth.setDecimals(1)
        bandwidth.setKeyboardTracking(False)
        bandwidth.setRange(*[self.conversion(r) for r in [self.ran[1],self.ran[0]]])
        bandwidth.setValue(initband)
        bandwidth.setSuffix('kHz')
        #connect
        duration.valueChanged.connect(self.onNewDuration)
        bandwidth.valueChanged.connect(self.onNewBandwidth)
        #add to layout
        layout.addWidget(durationLabel, 0, 0, 1, 1)
        layout.addWidget(bandwidthLabel, 0, 1, 1, 1)
        layout.addWidget(duration, 1, 0, 1, 1)
        layout.addWidget(bandwidth, 1, 1, 1, 1)
        self.setLayout(layout)
        self.show()
    
    def onNewDuration(self, dur):
        band = self.conversion(dur)
        self.bandwidth.blockSignals(True)
        self.bandwidth.setValue(band)
        self.bandwidth.blockSignals(False)
    
    def onNewBandwidth(self, ban):
        dur =  self.conversion(ban)
        self.duration.blockSignals(True)
        self.duration.setValue(dur)
        self.duration.blockSignals(False)
        
    @staticmethod
    def conversion(x):
        return 10**3 * (2 * numpy.pi / float(x)) #fourier bandwidth, and unit conversion
    
    def closeEvent(self, x):
        self.reactor.stop()
    
class limitsWidget(QtGui.QWidget):
    def __init__(self, reactor, abs_range = (150,250), parent=None):
        super(limitsWidget, self).__init__(parent)
        self.reactor = reactor
        self.absoluteRange = abs_range
        self.initializeGUI()
        
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        startLabel = QtGui.QLabel('Start')
        stopLabel = QtGui.QLabel('Stop')
        resolutionLabel =  QtGui.QLabel('Set Resolution')
        stepsLabel = QtGui.QLabel('Set Steps')
        finalResolutionLabel = QtGui.QLabel('Resolution')
        self.start = start = QtGui.QDoubleSpinBox()
        self.stop = stop = QtGui.QDoubleSpinBox()
        self.setresolution = setresolution = QtGui.QDoubleSpinBox()
        self.resolution = resolution = QtGui.QLineEdit()
        self.steps = steps = QtGui.QSpinBox()
        steps.setRange(1,1000)
        resolution.setReadOnly(True)
        for widget in [start, stop, setresolution, steps]:
            widget.setKeyboardTracking(False)
        for widget in [start, stop, setresolution]:
            widget.setDecimals(3)
            widget.setSuffix('MHz')
            widget.setSingleStep(0.01)
        for widget in [start, stop]:
            widget.setRange(*self.absoluteRange)
        start.setValue(self.absoluteRange[0])
        stop.setValue(self.absoluteRange[1])
        setresolution.setValue(self.absoluteRange[1] - self.absoluteRange[0])
        setresolution.setRange(10**-3, self.absoluteRange[1] - self.absoluteRange[0])
        self.updateResolution(setresolution.value())
        #connect
        start.valueChanged.connect(self.onNewStartStop)
        stop.valueChanged.connect(self.onNewStartStop)
        setresolution.valueChanged.connect(self.onNewResolution)
        steps.valueChanged.connect(self.onNewStartStop)
        #add to layout
        layout.addWidget(startLabel, 0, 0, 1, 1)
        layout.addWidget(stopLabel, 0, 1, 1, 1)
        layout.addWidget(resolutionLabel, 0, 2, 1, 1)
        layout.addWidget(stepsLabel, 0, 3, 1, 1)
        layout.addWidget(finalResolutionLabel, 0, 4, 1, 1)
        layout.addWidget(start, 1, 0, 1, 1)
        layout.addWidget(stop, 1, 1, 1, 1)
        layout.addWidget(setresolution, 1, 2, 1, 1)
        layout.addWidget(steps, 1, 3, 1, 1)
        layout.addWidget(resolution, 1, 4, 1, 1)
        self.setLayout(layout)
        self.show()
    
    def getValues(self):
        start = self.start.value()
        stop = self.stop.value()
        steps = self.steps.value()
        values = numpy.linspace(start, stop, steps, endpoint = True)
        return values
    
    def onNewStartStop(self, x):
        start = self.start.value()
        stop = self.stop.value()
        steps = self.steps.value()
        #update the ranges
        self.start.setRange(self.absoluteRange[0], stop)
        self.stop.setRange(start, self.absoluteRange[1])
        #calculate and update the actual resolution
        if steps > 1:
            res = numpy.linspace(start, stop, steps, endpoint = True, retstep = True)[1]
        else:
            res = stop - start
        self.setresolution.blockSignals(True)
        self.setresolution.setValue(res)
        self.setresolution.blockSignals(False)
        self.updateResolution(res)
    
    def updateResolution(self, val):
        text = '{:.3f} MHz'.format(val)
        self.resolution.setText(text)
    
    def onNewResolution(self, res):
        start = self.start.value()
        stop = self.stop.value()
        steps = 1 +  max(0, int(round( (stop - start) / res))) #make sure at least 1
        self.steps.blockSignals(True)
        self.steps.setValue(steps)
        self.steps.blockSignals(False)
        if steps > 1:
            finalres = numpy.linspace(start, stop, steps, endpoint = True, retstep = True)[1]
        else:
            finalres = stop - start
        self.updateResolution(finalres)
    
    def closeEvent(self, x):
        self.reactor.stop()
          
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = limitsWidget(reactor)
    #widget = durationWdiget(reactor)
    widget.show()
    reactor.run()