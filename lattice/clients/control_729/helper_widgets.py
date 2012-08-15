from PyQt4 import QtGui, QtCore
import numpy

class durationWdiget(QtGui.QFrame):
    def __init__(self, reactor, value = 1, init_range = (1,1000), parent=None):
        super(durationWdiget, self).__init__(parent)
        self.reactor = reactor
        self.value = value
        self.ran = init_range
        self.initializeGUI()
        
    def initializeGUI(self):
        self.setFrameShape(QtGui.QFrame.Box)
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
        return 10**3 * (1.0 / (2.0 * numpy.pi * float(x) ) ) #fourier bandwidth, and unit conversion
    
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
        self.start = start = QtGui.QDoubleSpinBox()
        self.stop = stop = QtGui.QDoubleSpinBox()
        self.center = center = QtGui.QDoubleSpinBox()
        self.span = span = QtGui.QDoubleSpinBox()
        self.setresolution = setresolution = QtGui.QDoubleSpinBox()
        self.resolution = resolution = QtGui.QLineEdit()
        self.steps = steps = QtGui.QSpinBox()
        steps.setRange(1,1000)
        resolution.setReadOnly(True)
        steps.setKeyboardTracking(False)
        for widget in [start, stop, setresolution, center, span]:
            widget.setKeyboardTracking(False)
            widget.setDecimals(3)
            widget.setSuffix('MHz')
            widget.setSingleStep(0.01)
        for widget in [start, stop]:
            widget.setRange(*self.absoluteRange)
        max_diff = self.absoluteRange[1] - self.absoluteRange[0]
        start.setValue(self.absoluteRange[0])
        stop.setValue(self.absoluteRange[1])
        span.setRange(-max_diff, max_diff)
        span.setValue(max_diff)
        center.setRange(self.absoluteRange[0], self.absoluteRange[1])
        center.setValue(self.absoluteRange[0] + max_diff / 2.0)
        setresolution.setRange(-max_diff, max_diff)
        setresolution.setValue(self.absoluteRange[1] - self.absoluteRange[0])
        self.updateResolution(setresolution.value())
        #connect
        start.valueChanged.connect(self.onNewStartStop)
        stop.valueChanged.connect(self.onNewStartStop)
        setresolution.valueChanged.connect(self.onNewResolution)
        steps.valueChanged.connect(self.onNewStartStop)
        span.valueChanged.connect(self.onNewCenterSpan)
        center.valueChanged.connect(self.onNewCenterSpan)
        #add to layout
        layout.addWidget( QtGui.QLabel('Start'), 0, 0, 1, 1)
        layout.addWidget(QtGui.QLabel('Stop'), 0, 1, 1, 1)
        layout.addWidget(QtGui.QLabel('Set Resolution'), 0, 2, 1, 1)
        layout.addWidget(QtGui.QLabel('Set Steps'), 0, 3, 1, 1)
        layout.addWidget(QtGui.QLabel('Resolution'), 0, 4, 1, 1)
        layout.addWidget(QtGui.QLabel('Center'), 2, 0, 1, 1)
        layout.addWidget(QtGui.QLabel('Span'), 2, 1, 1, 1)
        layout.addWidget(start, 1, 0, 1, 1)
        layout.addWidget(stop, 1, 1, 1, 1)
        layout.addWidget(setresolution, 1, 2, 1, 1)
        layout.addWidget(steps, 1, 3, 1, 1)
        layout.addWidget(resolution, 1, 4, 1, 1)
        layout.addWidget(center, 3, 0, 1, 1)
        layout.addWidget(span, 3, 1, 1, 1)
        self.setLayout(layout)
        self.show()
    
    def getValues(self):
        start = self.start.value()
        stop = self.stop.value()
        steps = self.steps.value()
        values = numpy.linspace(start, stop, steps, endpoint = True)
        return values
    
    def onNewCenterSpan(self, x):
        center = self.center.value()
        span = self.span.value()
        self.start.blockSignals(True)
        self.stop.blockSignals(True)
        self.start.setValue(center - span / 2.0)
        self.stop.setValue(center + span/2.0)
        self.start.blockSignals(False)
        self.stop.blockSignals(False)
    
    def onNewStartStop(self, x):
        start = self.start.value()
        stop = self.stop.value()
        steps = self.steps.value()
        #update center and span
        self.center.blockSignals(True)
        self.span.blockSignals(True)
        self.center.setValue((start + stop)/2.0)
        self.span.setValue(stop - start)
        self.center.blockSignals(False)
        self.span.blockSignals(False)
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


class saved_frequencies(QtGui.QTableWidget):
    def __init__(self, reactor, parent=None):
        super(saved_frequencies, self).__init__(parent)
        self.reactor = reactor
        self.initializeGUI()
        
    def initializeGUI(self):
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setColumnCount(2)
        self.fill_out_widget([('hi',220.0),('bye',230.0)])
    
    def fill_out_widget(self, info):
        self.clearContents()
        self.setRowCount(len(info))
        for enum,tup in enumerate(info):
            name,val = tup
            self.setItem(enum , 0 , QtGui.QTableWidgetItem(name))
            sample = QtGui.QDoubleSpinBox()
            sample.setRange(0,500)
            sample.setValue(val)
            self.setCellWidget(enum, 1, sample)
            
    def closeEvent(self, x):
        self.reactor.stop()

class saved_frequencies_dropdown(QtGui.QComboBox):
    
    selected_signal = QtCore.pyqtSignal(float)
    
    def __init__(self, reactor, parent=None):
        super(saved_frequencies_dropdown, self).__init__(parent)
        self.reactor = reactor
        self.initializeGUI()
        
    def initializeGUI(self):
        self.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.fill_out_widget([('hi',220.0),('bye',230.0)])
        self.currentIndexChanged.connect(self.on_select)
    
    def fill_out_widget(self, info):
        self.clear()
        for index,tup in enumerate(info):
            name,val = tup
            text = '{0}    :    {1}MHz'.format(name, val)
            self.addItem(text)
            self.setItemData(index, QtCore.QVariant(val))
    
    def on_select(self, index):
        val,ok = self.itemData(index).toFloat()
        self.selected_signal.emit(val)
        
    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    #widget = limitsWidget(reactor)
    #widget = durationWdiget(reactor)
    widget = saved_frequencies(reactor)
    widget = saved_frequencies_dropdown(reactor)
    widget.show()
    reactor.run()