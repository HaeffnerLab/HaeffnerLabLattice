import sys
from PyQt4 import QtGui, QtCore
from matplotlib.figure import Figure
from matplotlib import cm
import time
from twisted.internet.threads import deferToThread
from twisted.internet.defer import inlineCallbacks







from matplotlib.widgets import RectangleSelector 
import numpy as np

import pyqtgraph as pg

# class Canvas(FigureCanvas):
#     """Matplotlib Figure widget to display CPU utilization"""
#     def __init__(self, parent):
#         self.parent = parent
#         self.fig = Figure()
#         FigureCanvas.__init__(self, self.fig)
#         self.cnt = 0
#         
#         
#     def newAxes(self, data, hstart, hend, vstart, vend):
#         self.fig.clf()
#         self.ax = self.fig.add_subplot(111)
#         print hstart, hend, vstart, vend
#         data = np.reshape(data, ((vend-vstart+1), (hend-hstart+1)))
#         self.im = self.ax.imshow(data, extent=[hstart, hend, vstart, vend], origin='lower', interpolation='nearest')#, cmap=cm.hot)#gist_heat)
#         print 'happened once!'
#         self.setupSelector()
# 
#     def updateData(self, data, width, height):
# #        print 'i got called!'
#         try:
# #            self.data = np.reshape(data, (height, width))
#             data = np.reshape(data, (height, width))
#         except ValueError:
# #            print 'i dont get it' # happens if update data is called before the new width and height are calculated upon changing the image size
#             pass
# #        self.im.set_data(self.data)
#         self.im.set_data(data)
#         self.im.axes.figure.canvas.draw()
#   
#     def onselect(self, eclick, erelease):
#         'eclick and erelease are matplotlib events at press and release'
#         print ' startposition : (%f, %f)' % (eclick.xdata, eclick.ydata)
#         print ' endposition   : (%f, %f)' % (erelease.xdata, erelease.ydata)
#           
#         if (eclick.ydata > erelease.ydata):
#             eclick.ydata, erelease.ydata= erelease.ydata, eclick.ydata
#         if (eclick.xdata > erelease.xdata):
#             eclick.xdata, erelease.xdata = erelease.xdata, eclick.xdata
#         
#         # data sent will always have the eclick point be the left point and the erelease point be the right point
# #        self.parent.parent.changeImageRegion(int(eclick.xdata), int(eclick.ydata), int(erelease.xdata), int(erelease.ydata))
# 
#         self.parent.parent.hstart = int(eclick.xdata)
#         self.parent.parent.hend = int(erelease.xdata)
#         self.parent.parent.vstart = int(eclick.ydata)
#         self.parent.parent.vend = int(erelease.ydata)
#         
#         if (self.parent.parent.live == True):
#             self.parent.abortVideo(1)
#             self.parent.parent.width = int(erelease.xdata) - int(eclick.xdata)
#             self.parent.parent.height = int(erelease.ydata) - int(eclick.ydata)
#             self.parent.parent.parent.setDimensions((int(erelease.xdata) - int(eclick.xdata) + 1), (int(erelease.ydata) - int(eclick.ydata) + 1))
#             error = self.parent.parent.parent.SetImage(1,1,int(eclick.xdata),int(erelease.xdata),int(eclick.ydata),int(erelease.ydata))
#             print 'image: ', self.parent.parent.parent.imageRegion
#             self.parent.parent.liveVideo()
#         else:
#             self.parent.parent.width = int(erelease.xdata) - int(eclick.xdata)
#             self.parent.parent.height = int(erelease.ydata) - int(eclick.ydata)
#             self.parent.parent.parent.setDimensions((int(erelease.xdata) - int(eclick.xdata) + 1), (int(erelease.ydata) - int(eclick.ydata) + 1))
#             error = self.parent.parent.parent.SetImage(1,1,int(eclick.xdata),int(erelease.xdata),int(eclick.ydata),int(erelease.ydata))
#             print 'image: ', self.parent.parent.parent.imageRegion
#         
#     
#     def setupSelector(self):
#         self.rectSelect = RectangleSelector(self.ax, self.onselect, drawtype='box', rectprops = dict(facecolor='red', edgecolor = 'white',
#                  alpha=0.5, fill=False))     
#         
#     def clearData(self):
#         #del self.data
#         pass      
        
class AppWindow(QtGui.QWidget):
    """Creates the window for the new plot"""
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        
        self.parent = parent
        
        self.cmon = Canvas(self)
        self.cmon.show()
        # instantiate the navigation toolbar
        ntb = NavigationToolbar(self.cmon, self)
        
        layout = QtGui.QVBoxLayout()

        # Layout that involves the canvas, toolbar, graph options...etc.
        layout.addWidget(ntb)
        layout.addWidget(self.cmon)
        
        
        temperatureButton = QtGui.QPushButton("Temp", self)
        temperatureButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        temperatureButton.clicked.connect(self.printTemperature)     
        
        liveVideoButton = QtGui.QPushButton("Live", self)
        liveVideoButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        liveVideoButton.clicked.connect(self.liveVideo)
        
        abortButton = QtGui.QPushButton("Abort Video", self)
        abortButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        abortButton.clicked.connect(self.abortVideo)
        
        resetScaleButton = QtGui.QPushButton("Reset Scale", self)
        resetScaleButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        resetScaleButton.clicked.connect(self.resetScale)
        
        emGainLabel = QtGui.QLabel()
        emGainLabel.setText('EM Gain: ')
        
        self.emGainSpinBox = QtGui.QSpinBox()
        self.emGainSpinBox.setMinimum(0)
        self.emGainSpinBox.setMaximum(255)
        self.emGainSpinBox.setSingleStep(1)  
        self.emGainSpinBox.setValue(EMGAIN)     
        self.emGainSpinBox.setKeyboardTracking(False)
        self.connect(self.emGainSpinBox, QtCore.SIGNAL('valueChanged(int)'), self.changeEMGain)

        exposureLabel = QtGui.QLabel()
        exposureLabel.setText('Exposure (ms): ')
        
        

        
        # Layout
        self.bottomPanel1 = QtGui.QHBoxLayout()
        
        self.bottomPanel1.addWidget(temperatureButton)
        self.bottomPanel1.addWidget(liveVideoButton)
        self.bottomPanel1.addWidget(abortButton)
        self.bottomPanel1.addWidget(resetScaleButton)
        self.bottomPanel1.addWidget(emGainLabel)
        self.bottomPanel1.addWidget(self.emGainSpinBox)
        self.bottomPanel1.addWidget(exposureLabel)
        self.bottomPanel1.addWidget(self.exposureSpinBox)
    
        self.bottomPanel1.addStretch(0)
        self.bottomPanel1.setSizeConstraint(QtGui.QLayout.SetFixedSize)        
        layout.addLayout(self.bottomPanel1)
               
        self.setLayout(layout)

    def changeEMGain(self, value):
        self.parent.parent.ChangeEMCCDGain(self.emGainSpinBox.value())

    def changeExposure(self, value):
        if (self.parent.live == True):
            self.abortVideo(1)
            self.parent.parent.SetExposureTime(float(self.exposureSpinBox.value())/1000) #convert ms to s
            self.parent.exposureTime = float(self.exposureSpinBox.value())/1000
            self.parent.liveVideo()
        else:
            self.parent.parent.SetExposureTime(float(self.exposureSpinBox.value())/1000) #convert ms to s               

    def abortVideo(self, evt):
        self.parent.live = False
        self.parent.parent.AbortAcquisition()
        self.cmon.clearData()
        print 'Aborted!'

    def printTemperature(self, evt):
        tempError = self.parent.parent.GetCurrentTemperature()
        temp = self.parent.parent.currentTemperature
        print temp, tempError
   
    def liveVideo(self, evt):
        self.parent.liveVideo()
        
    def resetScale(self, evt):
        self.parent.hstart = self.parent.originalHStart
        self.parent.hend = self.parent.originalHEnd
        self.parent.vstart = self.parent.originalVStart
        self.parent.vend = self.parent.originalVEnd
        self.parent.width = self.parent.hend - self.parent.hstart
        self.parent.height = self.parent.vend - self.parent.vstart
        if (self.parent.live == True):
            self.abortVideo(1)
            self.parent.parent.setDimensions((self.parent.width + 1), (self.parent.height + 1))
            error = self.parent.parent.SetImage(1,1,self.parent.hstart,self.parent.hend,self.parent.vstart,self.parent.vend)
            print 'image: ', self.parent.parent.imageRegion
            self.parent.liveVideo()
        else:
            self.parent.parent.setDimensions((self.parent.width + 1), (self.parent.height + 1))
            error = self.parent.parent.SetImage(1,1,self.parent.hstart,self.parent.hend,self.parent.vstart,self.parent.vend)
            print 'image: ', self.parent.parent.imageRegion

        
    def closeEvent(self, evt):
        self.abortVideo(1)
        try:
            self.killTimer(self.cmon.timer)
        except AttributeError:
            pass 
          

class AndorVideo(QtGui.QWidget):
    def __init__(self, server):
        super(AndorVideo, self).__init__()
        from labrad.units import WithUnit
        self.WithUnit = WithUnit
        self.server = server
        self.setup_layout()
        self.connect_layout()
        
    def setup_layout(self):
        self.setWindowTitle("Andor")
        layout = QtGui.QGridLayout()
        graphics_view = pg.GraphicsView()
        #make a viewbox that goes inside the graphics_view
        vb = pg.ViewBox()
        vb.setAspectLocked()
        graphics_view.setCentralItem(vb)
        self.img = pg.ImageItem()
        vb.addItem(self.img)
        layout.addWidget(graphics_view, 0, 0, 1, 5)
        #histogram with the color bar
        w = pg.HistogramLUTWidget()
        w.setImageItem(self.img)
        w.setHistogramRange(0, 1000)
        layout.addWidget(w, 0, 5)
        #exposure
        exposure_label = QtGui.QLabel("Exposure")
        self.exposureSpinBox = QtGui.QDoubleSpinBox()
        self.exposureSpinBox.setSingleStep(0.1)
        self.exposureSpinBox.setMinimum(0.0)
        self.exposureSpinBox.setMaximum(10000.0)
        self.exposureSpinBox.setKeyboardTracking(False)
        self.exposureSpinBox.setSuffix(' ms')      
        layout.addWidget(exposure_label, 1, 4,)
        layout.addWidget(self.exposureSpinBox, 1, 5)
        #EMCCD Gain
        emccd_label = QtGui.QLabel("EMCCD Gain")
        self.emccdSpinBox = QtGui.QSpinBox()
        self.emccdSpinBox.setSingleStep(1)  
        self.emccdSpinBox.setMinimum(0)
        self.emccdSpinBox.setMaximum(255)
        self.emccdSpinBox.setKeyboardTracking(False)
        layout.addWidget(emccd_label, 2, 4,)
        layout.addWidget(self.emccdSpinBox, 2, 5)
        #Live Video Button
        self.live_button = QtGui.QPushButton("Live Video")
        self.live_button.setCheckable(True)
        layout.addWidget(self.live_button, 2, 0)
        #set the layout and show
        self.setLayout(layout)
        self.show()
    
    @inlineCallbacks
    def connect_layout(self):
        exposure = yield self.server.getExposureTime(None)
        self.exposureSpinBox.setValue(exposure['s'])     
        self.exposureSpinBox.valueChanged.connect(self.on_new_exposure)
        gain = yield self.server.getEMCCDGain(None)
        self.emccdSpinBox.setValue(gain)
        self.emccdSpinBox.valueChanged.connect(self.on_new_gain)
        self.live_button.clicked.connect(self.on_live_button)
    
    @inlineCallbacks
    def on_new_exposure(self, exposure):
        yield self.server.setExposureTime(None, self.WithUnit(exposure,'ms'))
    
    def set_exposure(self, exposure):
        self.exposureSpinBox.blockSignals(True)
        self.exposureSpinBox.setValue(exposure)
        self.exposureSpinBox.blockSignals(False)
    
    @inlineCallbacks
    def on_new_gain(self, gain):
        yield self.server.setEMCCDGain(None, gain)
    
    def set_gain(self, gain):
        self.emccdSpinBox.blockSignals(True)
        self.emccdSpinBox.setValue(gain)
        self.emccdSpinBox.blockSignals(False)
    
    @inlineCallbacks
    def on_live_button(self, checked):
        yield None
        print checked
        if checked:
            image = self.server
            yield self.server.startAcquisition(None)
            yield self.server.waitForAcquisition(None)
            data = yield self.server.getAcquiredData(None)
            binx,biny, startx, stopx, starty, stopy = yield self.server.getImageRegion(None)
            pixels_x = (stopx - startx + 1) / binx
            pixels_y = (stopy - starty + 1) / biny
            image_data = np.reshape(data, (pixels_x, pixels_y))
            print image_data.max(), image_data.min()
            self.img.setImage(image_data, autoLevels = False)
            

    @inlineCallbacks
    def liveVideo(self):
               
#        width = self.width
#        height = self.height
        
        print "Ready for Acquisition..."
        
        status = self.parent.GetStatus()
        if (self.parent.status == 'DRV_IDLE'):
            self.parent.SetAcquisitionMode(5)
            self.parent.StartAcquisition()
            try:
                newdata = self.parent.GetMostRecentImage()
                self.win.cmon.newAxes(newdata, self.hstart, self.hend, self.vstart, self.vend)
            except AttributeError:
                print 'yup outside the while'                    
            cnt = 0
            self.live = True
            while(self.live == True):
                yield deferToThread(time.sleep, self.exposureTime)
                newdata = self.parent.GetMostRecentImage()
                try:
#                    print 'call me maybe'
                    self.win.cmon.updateData(newdata, (self.width + 1), (self.height + 1))
#                    print width, height
#                    print self.width, self.height
                except AttributeError:
                    print 'yup in the while'
                    self.win.cmon.newAxes(newdata, self.hstart, self.hend, self.vstart, self.vend)
            self.parent.AbortAcquisition()      