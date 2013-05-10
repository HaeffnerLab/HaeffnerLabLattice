from PyQt4 import QtGui
from twisted.internet.defer import inlineCallbacks
import numpy as np
import pyqtgraph as pg

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
        graphics_view.addItem(vb)
        self.img = pg.ImageItem()
        vb.addItem(self.img)
        
        x_axis = pg.AxisItem('left')
        x_axis.linkToView(vb)
        vb.addItem(x_axis)
        
        
        layout.addWidget(graphics_view, 0, 0, 1, 5)
        #histogram with the color bar
        w = pg.HistogramLUTWidget()
        w.setImageItem(self.img)
        w.setHistogramRange(0, 1000)
        layout.addWidget(w, 0, 5)
        #exposure#         x_axis = pg.AxisItem('botton')
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
#         exposure = yield self.server.getExposureTime(None)
#         self.exposureSpinBox.setValue(exposure['s'])     
#         self.exposureSpinBox.valueChanged.connect(self.on_new_exposure)
#         gain = yield self.server.getEMCCDGain(None)
#         self.emccdSpinBox.setValue(gain)
#         self.emccdSpinBox.valueChanged.connect(self.on_new_gain)
        yield None
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
        if checked:
#             image = self.server
#             yield self.server.startAcquisition(None)
#             yield self.server.waitForAcquisition(None)
#             data = yield self.server.getAcquiredData(None)
#             binx,biny, startx, stopx, starty, stopy = yield self.server.getImageRegion(None)
#             pixels_x = (stopx - startx + 1) / binx
#             pixels_y = (stopy - starty + 1) / biny
#             image_data = np.reshape(data, (pixels_x, pixels_y))
#             print image_data.max(), image_data.min()
            image_data = np.random.random((100,100)) * 1000
            print image_data.shape
            self.img.setImage(image_data, autoLevels = False)