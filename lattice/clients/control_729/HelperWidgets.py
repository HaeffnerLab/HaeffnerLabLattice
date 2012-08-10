from PyQt4 import QtGui
import numpy

class durationWdiget(QtGui.QWidget):
    def __init__(self, value = 1, init_range = (1,1000), parent=None):
        super(durationWdiget, self).__init__(parent)
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
    
class limitsWidget(QtGui.QWidget):
    def __init__(self, abs_range = (150,250), parent=None):
        super(limitsWidget, self).__init__(parent)
        self.absoluteRange = abs_range
        self.initializeGUI()
        
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        startLabel = QtGui.QLabel('Start')
        stopLabel = QtGui.QLabel('Stop')
        resolutionLabel =  QtGui.QLabel('Resolution')
        stepsLabel = QtGui.QLabel('Steps')
        self.start = start = QtGui.QDoubleSpinBox()
        self.stop = stop = QtGui.QDoubleSpinBox()
        self.resolution = resolution = QtGui.QDoubleSpinBox()
        self.steps = steps = QtGui.QSpinBox()
        steps.setRange(1,1000)
        for widget in [start, stop, resolution, steps]:
            widget.setKeyboardTracking(False)
        for widget in [start, stop, resolution]:
            widget.setDecimals(3)
            widget.setSuffix('MHz')
        for widget in [start, stop]:
            widget.setRange(*self.absoluteRange)
        start.setValue(self.absoluteRange[0])
        stop.setValue(self.absoluteRange[1])
        resolution.setValue(self.absoluteRange[1] - self.absoluteRange[0])
        resolution.setRange(10**-3, self.absoluteRange[1] - self.absoluteRange[0])
        #connect
        start.valueChanged.connect(self.onNewStartStop)
        stop.valueChanged.connect(self.onNewStartStop)
        resolution.valueChanged.connect(self.onNewResolution)
        steps.valueChanged.connect(self.onNewSteps)
        #add to layout
        layout.addWidget(startLabel, 0, 0, 1, 1)
        layout.addWidget(stopLabel, 0, 1, 1, 1)
        layout.addWidget(resolutionLabel, 0, 2, 1, 1)
        layout.addWidget(stepsLabel, 0, 3, 1, 1)
        layout.addWidget(start, 1, 0, 1, 1)
        layout.addWidget(stop, 1, 1, 1, 1)
        layout.addWidget(resolution, 1, 2, 1, 1)
        layout.addWidget(steps, 1, 3, 1, 1)
        self.setLayout(layout)
        self.show()
    
    def getValues(self):
        pass
    
    def onNewStartStop(self, x):
        band = self.conversion(x)
        self.bandwidth.blockSignals(True)
        self.bandwidth.setValue(band)
        self.bandwidth.blockSignals(False)
    
    def onNewResolution(self, res):
        dur =  self.conversion(res)
        self.duration.blockSignals(True)
        self.duration.setValue(dur)
        self.duration.blockSignals(False)
        
    def onNewSteps(self, steps):
        pass
            
if __name__=="__main__":
    import sys
    app = QtGui.QApplication([])
    widget = limitsWidget((150.0,250.0))
    #widget = durationWdiget(30)
    sys.exit(app.exec_())
