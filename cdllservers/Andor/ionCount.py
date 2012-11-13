import sys
from PyQt4 import QtGui, QtCore
from matplotlib.figure import Figure
from matplotlib import cm
import time


from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread
from datetime import datetime

import numpy as np

EMGAIN = 255
EXPOSURE = .3 #sec
       
class Canvas(FigureCanvas):
    """Matplotlib Figure widget to display CPU utilization"""
    def __init__(self, darkIonCatalog):
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.hist(darkIonCatalog)

class HistWindow(QtGui.QWidget):        
    """Creates the window for the new plot"""
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        
        self.parent = parent
        
        layout = QtGui.QVBoxLayout()
        
        try:
            canvas = Canvas(self.parent.parent.darkIonCatalog)
        except AttributeError:
            raise Exception("Has a Dark Ion Catalog Been Retrieved?")
        canvas.show()
        ntb = NavigationToolbar(canvas, self)

        layout.addWidget(canvas)
        layout.addWidget(ntb)
        
        changeWindowTitleButton = QtGui.QPushButton("Change Window Title", self)
        changeWindowTitleButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        changeWindowTitleButton.clicked.connect(self.changeWindowTitle)
        
        layout.addWidget(changeWindowTitleButton)
        
        self.setLayout(layout)
        #self.show()
    
    def changeWindowTitle(self, evt):
        text, ok = QtGui.QInputDialog.getText(self, 'Change Window Name', 'Enter a name:')        
        if ok:
            text = str(text)
            self.setWindowTitle(text)
            
class AppWindow(QtGui.QWidget):
    """Creates the window for the new plot"""
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        
        self.parent = parent
        
        self.histList = []
        
       
        layout = QtGui.QVBoxLayout()
       
        
        temperatureButton = QtGui.QPushButton("Temp", self)
        temperatureButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        temperatureButton.clicked.connect(self.printTemperature)     
        
        getDarkIonCatalogButton = QtGui.QPushButton("Get Dark Ion Catalog", self)
        getDarkIonCatalogButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        getDarkIonCatalogButton.clicked.connect(self.getDarkIonCatalog) 
        
        collectDataButton = QtGui.QPushButton("Collect Data", self)
        collectDataButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        collectDataButton.clicked.connect(self.collectData)
#        collectDataButton.setEnabled(False)
        
        getIonPositionCatalogButton = QtGui.QPushButton("Get Ion Position Catalog", self)
        getIonPositionCatalogButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        getIonPositionCatalogButton.clicked.connect(self.getIonPositionCatalog)
        
        countDarkIonsButton = QtGui.QPushButton("Count Dark Ions", self)
        countDarkIonsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        countDarkIonsButton.clicked.connect(self.countDarkIons)
        
        openKineticButton = QtGui.QPushButton("Open Kinetic", self)
        openKineticButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        openKineticButton.clicked.connect(self.openKinetic)
        
        pathLabel = QtGui.QLabel()
        pathLabel.setText('Path: ')
        
        self.pathEdit = QtGui.QLineEdit()        
                        
        exposureLabel = QtGui.QLabel()
        exposureLabel.setText('Exposure (ms): ')

        iterationsLabel = QtGui.QLabel()
        iterationsLabel.setText('Iterations: ')
        
        ionThresholdLabel = QtGui.QLabel()
        ionThresholdLabel.setText('Ion Threshold: ')

        darkIonThresholdLabel = QtGui.QLabel()
        darkIonThresholdLabel.setText('Dark Ion Threshold: ')        
        
        self.exposureSpinBox = QtGui.QSpinBox()
        self.exposureSpinBox.setMinimum(100)
        self.exposureSpinBox.setMaximum(1000)
        self.exposureSpinBox.setSingleStep(1)  
        self.exposureSpinBox.setValue(EXPOSURE*1000)     
        self.exposureSpinBox.setKeyboardTracking(False)
        self.connect(self.exposureSpinBox, QtCore.SIGNAL('valueChanged(int)'), self.changeExposure)

        self.iterationsSpinBox = QtGui.QSpinBox()
        self.iterationsSpinBox.setMinimum(0)
        self.iterationsSpinBox.setMaximum(1000)
        self.iterationsSpinBox.setSingleStep(1)  
        self.iterationsSpinBox.setValue(2)     
        self.iterationsSpinBox.setKeyboardTracking(False)

        self.ionThresholdSpinBox = QtGui.QSpinBox()
        self.ionThresholdSpinBox.setMinimum(0)
        self.ionThresholdSpinBox.setMaximum(1000)
        self.ionThresholdSpinBox.setSingleStep(1)  
        self.ionThresholdSpinBox.setValue(500)     
        self.ionThresholdSpinBox.setKeyboardTracking(False)

        self.darkIonThresholdSpinBox = QtGui.QSpinBox()
        self.darkIonThresholdSpinBox.setMinimum(-1000)
        self.darkIonThresholdSpinBox.setMaximum(0)
        self.darkIonThresholdSpinBox.setSingleStep(1)  
        self.darkIonThresholdSpinBox.setValue(-200)     
        self.darkIonThresholdSpinBox.setKeyboardTracking(False)

        
        imageAnalyzedLabel = QtGui.QLabel()
        imageAnalyzedLabel.setText('Images to analyze: ')

        typIonDiameterLabel = QtGui.QLabel()
        typIonDiameterLabel.setText('Typical Ion Diameter: ')
        
        peakVicinityLabel = QtGui.QLabel()
        peakVicinityLabel.setText('Peak Vicinity: ')
        
        
        self.imageAnalyzedSpinBox = QtGui.QSpinBox()
        self.imageAnalyzedSpinBox.setMinimum(1)
        self.imageAnalyzedSpinBox.setMaximum(20)
        self.imageAnalyzedSpinBox.setSingleStep(1)  
        self.imageAnalyzedSpinBox.setValue(1)     
        self.imageAnalyzedSpinBox.setKeyboardTracking(False)        

        self.typIonDiameterSpinBox = QtGui.QSpinBox()
        self.typIonDiameterSpinBox.setMinimum(1)
        self.typIonDiameterSpinBox.setMaximum(20)
        self.typIonDiameterSpinBox.setSingleStep(1)  
        self.typIonDiameterSpinBox.setValue(5)     
        self.typIonDiameterSpinBox.setKeyboardTracking(False) 

        self.peakVicinitySpinBox = QtGui.QSpinBox()
        self.peakVicinitySpinBox.setMinimum(0)
        self.peakVicinitySpinBox.setMaximum(10)
        self.peakVicinitySpinBox.setSingleStep(1)  
        self.peakVicinitySpinBox.setValue(2)     
        self.peakVicinitySpinBox.setKeyboardTracking(False) 

         
         # Layout
        self.bottomPanel1 = QtGui.QHBoxLayout()
        
        self.bottomPanel1.addWidget(temperatureButton)
        self.bottomPanel1.addWidget(getDarkIonCatalogButton)
    
        self.bottomPanel1.addStretch(0)
        self.bottomPanel1.setSizeConstraint(QtGui.QLayout.SetFixedSize)        
        self.bottomPanel1.addWidget(iterationsLabel)
        self.bottomPanel1.addWidget(self.iterationsSpinBox)
        self.bottomPanel1.addWidget(ionThresholdLabel)
        self.bottomPanel1.addWidget(self.ionThresholdSpinBox)
        self.bottomPanel1.addWidget(darkIonThresholdLabel)
        self.bottomPanel1.addWidget(self.darkIonThresholdSpinBox)

        
        self.bottomPanel2 = QtGui.QHBoxLayout()

#        self.bottomPanel2.addStretch(0)
        self.bottomPanel2.addWidget(collectDataButton)
        self.bottomPanel2.addWidget(getIonPositionCatalogButton)
        self.bottomPanel2.addWidget(imageAnalyzedLabel)
        self.bottomPanel2.addWidget(self.imageAnalyzedSpinBox)
#        self.bottomPanel2.addWidget(exposureLabel)
#        self.bottomPanel2.addWidget(self.exposureSpinBox)
        self.bottomPanel2.addWidget(typIonDiameterLabel)
        self.bottomPanel2.addWidget(self.typIonDiameterSpinBox)
        self.bottomPanel2.addWidget(peakVicinityLabel)
        self.bottomPanel2.addWidget(self.peakVicinitySpinBox)
        
        self.bottomPanel3 = QtGui.QHBoxLayout()

        self.bottomPanel3.addWidget(countDarkIonsButton)
        self.bottomPanel3.addWidget(openKineticButton)
        self.bottomPanel3.addWidget(pathLabel)
        self.bottomPanel3.addWidget(self.pathEdit)
        

        layout.addLayout(self.bottomPanel1)
        layout.addLayout(self.bottomPanel2)
        layout.addLayout(self.bottomPanel3)
        
        self.setWindowTitle('Dark Ion Analysis')  
        self.setLayout(layout)

    def printTemperature(self, evt):
        self.parent.printTemperature()
    
    def getDarkIonCatalog(self, evt):
        self.parent.getDarkIonCatalog(self.imageAnalyzedSpinBox.value(), self.typIonDiameterSpinBox.value(), self.ionThresholdSpinBox.value(), self.darkIonThresholdSpinBox.value(), self.iterationsSpinBox.value())
        
    def getIonPositionCatalog(self, evt):
        self.parent.getIonPositionCatalog(self.imageAnalyzedSpinBox.value(), self.typIonDiameterSpinBox.value(), self.ionThresholdSpinBox.value(), self.darkIonThresholdSpinBox.value(), self.iterationsSpinBox.value(), self.peakVicinitySpinBox.value())
    
    def collectData(self, evt):
        self.parent.collectData(self.iterationsSpinBox.value(), self.imageAnalyzedSpinBox.value())
    
    def changeExposure(self, value):
        self.parent.changeExposure(float(self.exposureSpinBox.value())/1000) #convert ms to s     
        
    def countDarkIons(self):
        histWindow = HistWindow(self)
        self.histList.append(histWindow)
        histWindow.show()
        print np.mean(self.parent.darkIonCatalog)
    
    def openKinetic(self):
        self.parent.openKinetic(str(self.pathEdit.text()), ((self.imageAnalyzedSpinBox.value() + 1)*self.iterationsSpinBox.value()))

    def closeEvent(self, evt):
        self.parent.reactor.stop()           

class IonCount():
    def __init__(self, reactor):
        self.reactor = reactor
        self.live = False
        self.connect()

    def openVideoWindow(self):
        self.win = AppWindow(self)
        self.win.show()

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        try:
            self.server = yield self.cxn.andor_ion_count
            self.setupCamera()
        except Exception ,e:
            print 'server not connected: {}'.format(e)
   
    @inlineCallbacks
    def setupCamera(self):
        temp = yield self.server.get_current_temperature()
        print temp
        
        try:
            yield self.server.set_trigger_mode(0)
        except:
            print 'client not closed properly'
            self.abortVideo()
            yield self.server.set_trigger_mode(0)
        yield self.server.set_read_mode(4)
        yield self.server.set_emccd_gain(EMGAIN)
        yield self.server.set_exposure_time(EXPOSURE)   
        yield self.server.cooler_on()
        
        
        #self.detectorDimensions = yield self.server.get_detector_dimensions() #this gives a type error?
        
        self.hstart = 496#1
        self.hend = 536#141
        self.vstart = 155#1
        self.vend = 172#52
        
        self.width = self.hend - self.hstart
        self.height = self.vend - self.vstart
        
        print 'width: ', self.width
        print 'height: ', self.height
        
        error = yield self.server.set_image_region(1,1,self.hstart,self.hend,self.vstart,self.vend)
        print 'image: ', error
        
        self.openVideoWindow()

        
    @inlineCallbacks
    def printTemperature(self):
        temp = yield self.server.get_current_temperature()
        print temp
    
    @inlineCallbacks
    def collectData(self, iterations, numAnalyzedImages):
        yield self.server.collect_data((self.height + 1), (self.width + 1), iterations, numAnalyzedImages)
    
    @inlineCallbacks
    def getDarkIonCatalog(self, numAnalyzedImages, typicalIonDiameter, initialThreshold, darkThreshold, iterations):
        numKin =  (numAnalyzedImages + 1)*iterations
        self.darkIonCatalog = yield self.server.get_dark_ion_catalog(numKin, (self.height + 1), (self.width + 1), typicalIonDiameter, initialThreshold, darkThreshold, iterations)
        print self.darkIonCatalog

    @inlineCallbacks
    def getIonPositionCatalog(self, numAnalyzedImages, typicalIonDiameter, initialThreshold, darkThreshold, iterations, peakVicinity):
        numKin =  (numAnalyzedImages + 1)*iterations
        ionPositionCatalog = yield self.server.get_ion_position_catalog(numKin, (self.height + 1), (self.width + 1), typicalIonDiameter, initialThreshold, darkThreshold, iterations, peakVicinity)
        
        print ionPositionCatalog.asarray
    
    @inlineCallbacks
    def changeEMGain(self, value):
        yield self.server.set_emccd_gain(value)

    @inlineCallbacks
    def changeExposure(self, value):
        yield self.server.set_exposure_time(value)
        
    @inlineCallbacks
    def openKinetic(self, path, numKin):
        yield self.server.open_as_text_kinetic(path, numKin)
        print 'opened!'
    
    
    @inlineCallbacks
    def abortVideo(self):
        self.live = False
        yield self.server.abort_acquisition()
        print 'aborted'
               
if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    ionCount = IonCount(reactor)
    reactor.run()
    
