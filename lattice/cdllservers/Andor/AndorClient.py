import time
import sys
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from pylab import *
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue


class AndorClient(QtGui.QWidget):
    def __init__(self, reactor):
        QtGui.QWidget.__init__(self)
        self.reactor = reactor
        self.connect()

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        try:
            self.server = yield self.cxn.andor_server
            self.setupCamera()
        except Exception ,e:
            print 'server not connected: {}'.format(e)

    @inlineCallbacks
    def setupCamera(self):
        yield self.server.set_trigger_mode(0)
        yield self.server.set_read_mode(4)

        yield self.server.set_emccd_gain(255)
        yield self.server.set_exposure_time(.3)      
        yield self.server.cooler_on()
        
        imageRegion = yield self.server.get_image_region()
        self.width = imageRegion[3]
        self.height = imageRegion[5]
               
        self.setupUI()

    def setupUI(self):
        
        temperatureButton = QtGui.QPushButton("Temp", self)
        temperatureButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        temperatureButton.clicked.connect(self.printTemperature)     
        
        liveVideoButton = QtGui.QPushButton("Live", self)
        liveVideoButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        liveVideoButton.clicked.connect(self.liveVideo)
        
        singleButton = QtGui.QPushButton("Single", self)
        singleButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        singleButton.clicked.connect(self.singleScan)

        
         # Layout
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)
        self.grid.setSpacing(5)
        
        self.grid.addWidget(temperatureButton, 0, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(liveVideoButton, 0, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(singleButton, 0, 2, QtCore.Qt.AlignCenter)

        self.show()

    @inlineCallbacks
    def printTemperature(self, evt):
        temp = yield self.server.get_current_temperature()
        print temp

    
    @inlineCallbacks
    def liveVideo(self, evt):
        
        width = self.width
        height = self.height

        fig, ax = plt.subplots()
        
        newdata = np.zeros(width*height)
        newdata = np.reshape(newdata, (height, width))
        
        im = ax.matshow(newdata)
        fig.show()        
        
        print "Ready for Acquisition..."
        
        status = yield self.server.get_status()
        if (status == 'DRV_IDLE'):
            yield self.server.set_acquisition_mode(5)
            yield self.server.start_acquisition()
            for i in range(100):
                print i
                result = yield self.server.wait_for_acquisition()
                print result
                if (result == 'DRV_SUCCESS'):
            
                    data = yield self.server.get_most_recent_image()
                    newdata = np.array(data)
                    newdata = np.reshape(newdata, (height, width))
                    
                    im.set_array(newarray)
                    fig.canvas.draw()

    @inlineCallbacks
    def singleScan(self, evt):
        
        width = self.width
        height = self.height

        fig, ax = plt.subplots()
          
        print "Ready for Acquisition..."
        
        status = yield self.server.get_status()
        if (status == 'DRV_IDLE'):
            yield self.server.set_acquisition_mode(1)
            yield self.server.start_acquisition()
            result = yield self.server.wait_for_acquisition()
            if (result == 'DRV_SUCCESS'):
                data = yield self.server.get_acquired_data()
                newdata = np.array(data)
                newdata = np.reshape(newdata, (height, width))
                ax.matshow(newdata)
                
        fig.show()
    def closeEvent(self, evt):
        self.shutdown()
        
    @inlineCallbacks
    def shutdown(self):
        yield self.server.shutdown()
        
if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    Camera = AndorClient(reactor)
    reactor.run()