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
from twisted.internet.threads import deferToThread
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

from matplotlib.figure import Figure

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

class Qt4MplCanvas(FigureCanvas):
    def __init__(self, parent):

        print 'initialized'
        self.fig = Figure()

        #self.fig, self.ax = plt.subplots()

        self.ax = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.setup()
        
    def setup(self):
        newdata = np.zeros(658*496)
        newarray = np.reshape(newdata, (496, 658))
        self.im = self.ax.matshow(newarray)

        buttonax = self.fig.add_axes([0.45, 0.9, 0.1, 0.075])
        self.button = Button(buttonax, 'Update')
        self.button.on_clicked(self.update)
                
    def update(self, event):
        print 'redrawn?'
        self.im.set_data(self.data)
        self.draw()

    def updateData(self, data):
        print 'updated!'
        self.data = data
#        self.im.set_data(self.data)
#        self.draw()


class VideoWindow(QtGui.QMainWindow):
#    def __init__(self):
#        QtGui.QWidget.__init__(self)
#        layout = QtGui.QVBoxLayout()
#    
#        self.qmc = Qt4MplCanvas()
#        # instantiate the navigation toolbar
#        ntb = NavigationToolbar(self.qmc, self)
#    
#        # Layout that involves the canvas, toolbar, graph options...etc.
#        layout.addWidget(ntb)
#        layout.addWidget(self.qmc)
#        
#        self.setLayout(layout)

    """Example main window"""
    def __init__(self):
        # initialization of Qt MainWindow widget
        QtGui.QMainWindow.__init__(self)
        # set window title
        self.setWindowTitle("Matplotlib Figure in a Qt4 Window With NavigationToolbar")
        # instantiate a widget, it will be the main one
        self.main_widget = QtGui.QWidget(self)
        # create a vertical box layout widget
        vbl = QtGui.QVBoxLayout(self.main_widget)
        # instantiate our Matplotlib canvas widget
        self.qmc = Qt4MplCanvas(self.main_widget)
        # instantiate the navigation toolbar
        ntb = NavigationToolbar(self.qmc, self.main_widget)
        # pack these widget into the vertical box
        vbl.addWidget(self.qmc)
        vbl.addWidget(ntb)
        # set the focus on the main widget
        self.main_widget.setFocus()
        # set the central widget of MainWindow to main_widget
        self.setCentralWidget(self.main_widget)
#class planB():
#    def __init__(self):
#            
#        fig = plt.figure()
#                      
#        newdata = np.zeros(658*496)
#        newarray = np.reshape(newdata, (496, 658))
#        im = plt.imshow(newarray)
#        
#        def updatefig(*args):
#            try:
#                print 'data:',Camera.data[0,5]
#                im.set_array(Camera.data)
#            except AttributeError:
#                print 'nope'                    
#            return im,
#        
#        ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True)
#        plt.show()


#class DummyPlot(object):
#    def __init__(self):
#        self.imsize = (10, 10)
#        self.fig, self.ax = plt.subplots()
# 
#        self.ax.axis([0, 658, 0, 496])
#        self.ax.set_aspect(1.0)
#        self.ax.autoscale(False)
#        
#        newdata = np.zeros(658*496)
#        newarray = np.reshape(newdata, (496, 658))
#        self.data = newarray 
# 
#        self.im = self.ax.matshow(self.data)
#        
#        buttonax = self.fig.add_axes([0.45, 0.9, 0.1, 0.075])
#        self.button = Button(buttonax, 'Update')
#        self.button.on_clicked(self.update)
# 
#    def update(self, event):
#        #self.ax.matshow(self.data)
#        #self.ax.matshow(Camera.data)
#        self.im.set_data(self.data)
#        self.fig.canvas.draw()
#        
#    def updateData(self, data):
#        self.data = data
#        self.update(1)
# 
#    def show(self):
#        plt.show()
#        
#class planC():
#    def __init__(self):
#        
#        newdata = np.zeros(658*496)
#        newarray = np.reshape(newdata, (496, 658))
#        self.data = newarray 
#        
#        self.animate()
#    
#    def updateData(self, data):
#        print 'updated!'
#        self.data = data
#        print self.data[5, 1:4]     
#        
#    def animate(self):
#        
#        fig = plt.figure()
#        
#       
#        im = plt.matshow(self.data)
#        
#        def updatefig(*args):
#            im.set_array(self.data)
#            return im,
#
#        ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True)
#        plt.show()
#        
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
        
        print 'width: ', self.width
        print 'height: ', self.height
        
        error = yield self.server.set_image_region(1,1,1,self.width,1,self.height)
        print 'image error: ', error
        
#        input = int(raw_input("enter a number: "))
#        
#        if (input == 1):
#            self.printTemperature(1)
#        elif (input == 2):
#            self.liveVideo(1)
#        elif (input == 3):
#            self.singleScan(1)
#        elif (input == 4):
#            self.abort(1)        
               

        videoWindow = VideoWindow()
        videoWindow.show()

        #self.setupUI()


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
        
        abortButton = QtGui.QPushButton("Abort", self)
        abortButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        abortButton.clicked.connect(self.abort)        

        
         # Layout
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)
        self.grid.setSpacing(5)
        
        self.grid.addWidget(temperatureButton, 0, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(liveVideoButton, 0, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(singleButton, 0, 2, QtCore.Qt.AlignCenter)
        self.grid.addWidget(abortButton, 0, 3, QtCore.Qt.AlignCenter)

        self.show()

    @inlineCallbacks
    def abort(self, evt):
        print 'aborted'
        yield self.server.abort_acquisition()

    @inlineCallbacks
    def printTemperature(self, evt):
        temp = yield self.server.get_current_temperature()
        print temp

    
    @inlineCallbacks
    def liveVideo(self, evt):
        

#        d = DummyPlot()
#        d.show()
#        c = planC()
        width = self.width
        height = self.height

        #fig, ax = plt.subplots()
              
        newdata = np.zeros(width*height)
        newarray = np.reshape(newdata, (height, width))
        
        #im = ax.matshow(newarray)
        
        #fig.show()        
       
        print "Ready for Acquisition..."
        
        status = yield self.server.get_status()
        if (status == 'DRV_IDLE'):
            yield self.server.set_acquisition_mode(5)
            yield self.server.start_acquisition()
            for i in range(100):
                print i
                data = yield self.server.get_most_recent_image()
                newdata = data.asarray
                print newdata.shape
                newarray = np.reshape(newdata, (height, width))
                
                videoWindow.qmc.updateData(newarray)
                #im.set_data(newarray)
                #fig.canvas.draw()
        
    @inlineCallbacks
    def singleScan(self, evt):
        
        width = self.width
        height = self.height

        fig, ax = plt.subplots()
          
        print "Ready for Acquisition..."
        
        status = yield self.server.get_status()
        if (status == 'DRV_IDLE'):
            yield self.server.set_acquisition_mode(1)
            yield self.server.get_acquisition_mode()
            yield self.server.start_acquisition()
            data = yield self.server.get_acquired_data()
            newdata = data.asarray
            print newdata.shape
            newarray = np.reshape(newdata, (height, width))
            ax.matshow(newarray)
                
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