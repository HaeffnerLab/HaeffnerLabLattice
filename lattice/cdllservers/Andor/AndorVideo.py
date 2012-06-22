#import numpy as np
#import time
#from PyQt4 import QtGui, QtCore
#
#from twisted.internet.defer import inlineCallbacks, returnValue
#from twisted.internet.threads import deferToThread
#
#import matplotlib
#matplotlib.use('Qt4Agg')
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
#
#class Qt4MplCanvas(FigureCanvas):
#    def __init__(self, camera):
#
#        self.fig = Figure()
#
#        FigureCanvas.__init__(self, self.fig)
#        #self.fig, self.ax = plt.subplots()
#
#        self.ax = self.fig.add_subplot(111)
#        self.ax.axis([0, 658, 0, 496])
#        self.ax.set_aspect(1.0)
#        self.ax.autoscale(False)
#        newdata = np.ones(658*496)
#        newarray = np.reshape(newdata, (496, 658))
#        self.im = self.ax.matshow(newarray)
#              
#    def update(self, event):
#        print 'redrawn?'
#        self.im.set_data(camera.data)
#        self.im.axes.figure.canvas.draw()
#        
#class VideoWindow(QtGui.QWidget):
#    def __init__(self, camera):
#        QtGui.QWidget.__init__(self)
#        layout = QtGui.QVBoxLayout()
#    
#        self.qmc = Qt4MplCanvas(camera)
#        # instantiate the navigation toolbar
#        ntb = NavigationToolbar(self.qmc, self)
#        
#        Button = QtGui.QPushButton("Update", self)
#        Button.setGeometry(QtCore.QRect(0, 0, 30, 30))
#        Button.clicked.connect(self.qmc.update)        
#    
#        # Layout that involves the canvas, toolbar, graph options...etc.
#        layout.addWidget(ntb)
#        layout.addWidget(self.qmc)
#        layout.addWidget(Button)
#        
#        self.setLayout(layout)
#
#class AndorClient():
#    def __init__(self, reactor):
#        self.reactor = reactor
#        #self.connect()
#
#    @inlineCallbacks
#    def connect(self):
#        from labrad.wrappers import connectAsync
#        from labrad.types import Error
#        self.cxn = yield connectAsync()
#        try:
#            self.server = yield self.cxn.andor_server
#            self.setupCamera()
#        except Exception ,e:
#            print 'server not connected: {}'.format(e)
#
#    @inlineCallbacks
#    def setupCamera(self):
#        temp = yield self.server.get_current_temperature()
#        print temp
#
#        yield self.server.set_trigger_mode(0)
#        yield self.server.set_read_mode(4)
#
#        yield self.server.set_emccd_gain(255)
#        yield self.server.set_exposure_time(.3)      
#        yield self.server.cooler_on()
#        
#        
#        imageRegion = yield self.server.get_image_region()
#        self.width = imageRegion[3]
#        self.height = imageRegion[5]
#        
#        print 'width: ', self.width
#        print 'height: ', self.height
#        
#        error = yield self.server.set_image_region(1,1,1,self.width,1,self.height)
#        print 'image error: ', error
#        
#        self.liveVideo()
#
#    @inlineCallbacks
#    def liveVideo(self):
#        
#        time.sleep(5)
#        
#        width = self.width
#        height = self.height
#             
##        newdata = np.zeros(width*height)
##        newarray = np.reshape(newdata, (height, width))
#        
#
#        print "Ready for Acquisition..."
#        
#        status = yield self.server.get_status()
#        if (status == 'DRV_IDLE'):
#            yield self.server.set_acquisition_mode(5)
#            yield self.server.start_acquisition()
#            for i in range(10):
#                print i
#                data = yield self.server.get_most_recent_image()
#                newdata = data.asarray
#                print newdata.shape
#                self.data = newdata
#                newarray = np.reshape(newdata, (height, width))
#                print newarray[0, 4:7]
#                self.data = newarray
#            yield self.server.abort_acquisition()
#
#        
#if __name__ == "__main__":
#    a = QtGui.QApplication( [] )
#    import qt4reactor
#    qt4reactor.install()
#    from twisted.internet import reactor
#    Camera = AndorClient(reactor)
#    videoWindow = VideoWindow(Camera)
#    videoWindow.show()
#    reactor.run()










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




from matplotlib.widgets import RectangleSelector 
import numpy as np

EMGAIN = 255
EXPOSURE = .3 #sec

class Canvas(FigureCanvas):
    """Matplotlib Figure widget to display CPU utilization"""
    def __init__(self, parent):

        self.parent = parent
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        #self.cidPress = self.mpl_connect('button_press_event', self.onClick)
        #self.cidRelease = self.mpl_connect('button_release_event', self.onRelease)


        #self.X = np.random.rand(5,5)
        #rows,cols,self.slices = self.X.shape
        #self.Y = np.random.rand(5,5)
        #rows,cols,self.slices = self.X.shape
        
        newdata = np.ones(2*2)
        newarray = np.reshape(newdata, (2, 2))
        self.data = newarray

        
        #self.im = self.ax.matshow(self.X[:,:])
        #self.im = self.ax.matshow(self.data)
        self.update()
        
        self.fig.canvas.draw()

        self.cnt = 0
        
        self.setupSelector()
        # call the update method (to speed-up visualization)
        #self.timerEvent(None)
        # start timer, trigger event every 1000 millisecs (=1sec)
        #self.timer = self.startTimer(500)

#    def startYourEngines(self):
#        self.timer = self.startTimer(50)
    
#    def timerEvent(self, evt):
##        if (self.cnt == 12):
##            self.im = self.ax.matshow(self.data)
##            
##        
###        if (self.cnt == 0):
###            self.cnt = 1
###            self.im.set_data(self.X)
###        elif (self.cnt == 1):
###            self.im.set_data(self.Y)
###            self.cnt = 0    
##        elif (self.cnt > 12):    
##            self.im.set_data(self.data)            
##            #print self.data[0, 4:10]
##            
##            self.im.axes.figure.canvas.draw()
#        try: 
#            self.im.set_data(self.data)
#            self.im.axes.figure.canvas.draw()
#        except AttributeError:
#            self.im = self.ax.matshow(self.data)
#            self.im.axes.figure.canvas.draw()
#        
#        self.cnt += 1
        

#    def onClick(self, event):
#        print 'click: ', event.xdata, event.ydata
#    
#    def onRelease(self, event):
#        print 'release: ', event.xdata, event.ydata

    def updateData(self, data, width, height):
        try:
            self.data = np.reshape(data, (height, width))
        except ValueError:
            pass # happens if update data is called before the new width and height are calculated upon changing the image size
        try: 
            self.im.set_data(self.data)
            self.im.axes.figure.canvas.draw()
        except AttributeError:
            self.im = self.ax.matshow(self.data, cmap=cm.hot)#gist_heat)
            #self.ax.axis([self.parent.parent.hstart, self.parent.parent.hend, self.parent.parent.vstart, self.parent.parent.vend])
            self.im.axes.figure.canvas.draw()
    
    def onselect(self, eclick, erelease):
        'eclick and erelease are matplotlib events at press and release'
        print ' startposition : (%f, %f)' % (eclick.xdata, eclick.ydata)
        print ' endposition   : (%f, %f)' % (erelease.xdata, erelease.ydata)
          
        if (eclick.ydata > erelease.ydata):
            eclick.ydata, erelease.ydata= erelease.ydata, eclick.ydata
        if (eclick.xdata > erelease.xdata):
            eclick.xdata, erelease.xdata = erelease.xdata, eclick.xdata
        
        # data sent will always have the eclick point be the left point and the erelease point be the right point
        self.parent.parent.changeImageRegion(int(eclick.xdata), int(eclick.ydata), int(erelease.xdata), int(erelease.ydata))
        self.ax.axis([int(eclick.xdata), int(erelease.xdata), int(eclick.ydata), int(erelease.ydata)])

    
    def setupSelector(self):
        self.rectSelect = RectangleSelector(self.ax, self.onselect, drawtype='box', rectprops = dict(facecolor='red', edgecolor = 'white',
                 alpha=0.5, fill=False))           
        
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
        
        singleButton = QtGui.QPushButton("Single", self)
        singleButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        singleButton.clicked.connect(self.singleScan)
        
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
        
        self.exposureSpinBox = QtGui.QSpinBox()
        self.exposureSpinBox.setMinimum(0)
        self.exposureSpinBox.setMaximum(1000)
        self.exposureSpinBox.setSingleStep(1)  
        self.exposureSpinBox.setValue(EXPOSURE*1000)     
        self.exposureSpinBox.setKeyboardTracking(False)
        self.connect(self.exposureSpinBox, QtCore.SIGNAL('valueChanged(int)'), self.changeExposure)

        
         # Layout
        self.bottomPanel = QtGui.QHBoxLayout()
        
        self.bottomPanel.addWidget(temperatureButton)
        self.bottomPanel.addWidget(liveVideoButton)
        self.bottomPanel.addWidget(abortButton)
        self.bottomPanel.addWidget(resetScaleButton)
        self.bottomPanel.addWidget(singleButton)
        self.bottomPanel.addWidget(emGainLabel)
        self.bottomPanel.addWidget(self.emGainSpinBox)
        self.bottomPanel.addWidget(exposureLabel)
        self.bottomPanel.addWidget(self.exposureSpinBox)
    
        self.bottomPanel.addStretch(0)
        self.bottomPanel.setSizeConstraint(QtGui.QLayout.SetFixedSize)        
        layout.addLayout(self.bottomPanel)
        
        self.setLayout(layout)

    def changeEMGain(self, value):
        self.parent.changeEMGain(self.emGainSpinBox.value())

    def changeExposure(self, value):
        self.parent.changeExposure(float(self.exposureSpinBox.value())/1000) #convert ms to s       

    def abortVideo(self, evt):
        self.parent.abortVideo()

    def printTemperature(self, evt):
        self.parent.printTemperature()
    
    def singleScan(self, evt):
        self.parent.singleScan()
    
    def liveVideo(self, evt):
        self.parent.liveVideo()
        
    def resetScale(self, evt):
        self.parent.changeImageRegion(self.parent.originalHStart,self.parent.originalVStart,self.parent.originalHEnd,self.parent.originalVEnd)
        self.cmon.ax.axis([self.parent.originalHStart, self.parent.originalHEnd, self.parent.originalVStart, self.parent.originalVEnd])
    
    def closeEvent(self, evt):
        self.parent.abortVideo()
        try:
            self.killTimer(self.cmon.timer)
        except AttributeError:
            pass 
        self.parent.reactor.stop()           

class AndorClient():
    def __init__(self, reactor):
        self.reactor = reactor
        self.live = False
        self.openVideoWindow()
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
            self.server = yield self.cxn.andor_server
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

        # original window size can be changed here
        self.originalHStart = 1
        self.originalHEnd = 658#self.detectorDimensions[0]
        self.originalVStart = 1
        self.originalVEnd = 496#self.detectorDimensions[1]      
        
        self.hstart = self.originalHStart
        self.hend = self.originalHEnd
        self.vstart = self.originalVStart
        self.vend = self.originalVEnd
        
        self.width = self.hend - self.hstart
        self.height = self.vend - self.vstart
        
        print 'width: ', self.width
        print 'height: ', self.height
        
        error = yield self.server.set_image_region(1,1,self.hstart,self.hend,self.vstart,self.vend)
        print 'image: ', error
        
    @inlineCallbacks
    def printTemperature(self):
        temp = yield self.server.get_current_temperature()
        print temp
    
    @inlineCallbacks
    def singleScan(self):
        
#        width = self.width
#        height = self.height
#
##        fig, ax = plt.subplots()
#          
#        print "Ready for Acquisition..."
#        
#        status = yield self.server.get_status()
#        if (status == 'DRV_IDLE'):
#            yield self.server.set_acquisition_mode(1)
#            yield self.server.get_acquisition_mode()
#            yield self.server.start_acquisition()
#            data = yield self.server.get_acquired_data()
#            newdata = data.asarray
#            print 'Acquired'

        
        width = np.arange(self.width + 1) + 1
        height = np.arange(self.height + 1) + 1

        lenWidth = len(width)
        lenHeight = len(height)

        Width = np.ravel([width]*lenHeight)

        #This is slower! and wrong!
#        Height = np.zeros(lenWidth*lenHeight).reshape(lenHeight, lenWidth)
#        for i in Width:
#            for j in np.arange(lenWidth):
#                #print (i -1), j
#                Height[(i - 1), j] = i
#        Height = np.ravel(Height)
        Height = []
        for i in width:
            Height.append([i]*lenHeight)
        Height = np.ravel(np.array(Height))
        
        yield self.cxn.data_vault.cd('Camera Snapshots')
        t = datetime.now()
        dateTime = str(t.strftime("%Y-%m-%d %H:%M:%S"))
#        yield self.cxn.data_vault.new('Half-Life', [('x', 'in')], [('y','','in')])         
#        yield self.cxn.data_vault.add([[0.0,0.2],[1.0,0.2],[2.4,2.3],[3.3,0.0],[4.7,0.4],[4.5,1.2],[3.8,1.0],[2.3,4.8],[1.1,4.8],[1.1,4.1],[1.7,4.1],[2.0,3.4],[0.0,0.2]] )
        yield self.cxn.data_vault.new(dateTime, [('Pixels', '')], [('Pixels','',''), ('Counts','','')])         
        toDataVault = np.array(np.vstack((Height, Width, self.newdata)).transpose(), dtype=float)
        yield self.cxn.data_vault.add(toDataVault)
        print 'saved!'
#            newarray = np.reshape(newdata, (height, width))
#            ax.matshow(newarray)
#                
#        fig.show()
    
    
    @inlineCallbacks
    def liveVideo(self):
               
        width = self.width
        height = self.height
             
#        newdata = np.zeros(width*height)
#        newarray = np.reshape(newdata, (height, width))
        
        print "Ready for Acquisition..."
        
        status = yield self.server.get_status()
        if (status == 'DRV_IDLE'):
            yield self.server.set_acquisition_mode(5)
            yield self.server.start_acquisition()
            cnt = 0
            self.live = True
            while(self.live == True):
#                t1 = time.clock()
                data = yield self.server.get_most_recent_image()
                self.newdata = data.asarray
#                print newdata.shape
#                t2 = time.clock()
#                print 'Acquisition Time: ', (t2 - t1)
                #self.data = newdata
                #newarray = np.reshape(newdata, (height, width))
                #print newarray[0, 4:7]
                #self.data = newarray
                self.win.cmon.updateData(self.newdata, (self.width + 1), (self.height + 1))
#                if (cnt == 0):
#                    self.win.cmon.startYourEngines()
#                    cnt += 1
            yield self.server.abort_acquisition()
            
    @inlineCallbacks
    def changeEMGain(self, value):
        yield self.server.set_emccd_gain(value)

    @inlineCallbacks
    def changeExposure(self, value):
        if (self.live == True):
            self.abortVideo()
            yield self.server.set_exposure_time(value)
            self.liveVideo()
        else:
            yield self.server.set_exposure_time(value)
       
    
    @inlineCallbacks
    def abortVideo(self):
        self.live = False
        yield self.server.abort_acquisition()
        print 'aborted'
        
    @inlineCallbacks
    def changeImageRegion(self, xleft, yleft, xright, yright):
        self.hstart = xleft
        self.hend = xright
        self.vstart = yleft
        self.vend = yright
        self.width = self.hend - self.hstart
        self.height = self.vend - self.vstart
        if (self.live == True):
            self.abortVideo()
            error = yield self.server.set_image_region(1,1,self.hstart,self.hend,self.vstart,self.vend)
            print 'image: ', error
            self.liveVideo()
        else:
            error = yield self.server.set_image_region(1,1,self.hstart,self.hend,self.vstart,self.vend)
            print 'image error: ', error     
    
if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    Camera = AndorClient(reactor)
    reactor.run()
    
#import numpy
#from matplotlib.pyplot import figure, show
#
#
#
#
#class IndexTracker:
#    def __init__(self, ax, X):
#        self.ax = ax
#        ax.set_title('use scroll wheel to navigate images')
#
#        self.X = X
#        rows,cols,self.slices = X.shape
#        self.ind  = self.slices/2
#
#        self.im = ax.matshow(self.X[:,:,self.ind])
#        self.update()
#
#    def onscroll(self, event):
#        print event.button, event.step
#        if event.button=='up':
#            self.ind = numpy.clip(self.ind+1, 0, self.slices-1)
#        else:
#            self.ind = numpy.clip(self.ind-1, 0, self.slices-1)
#
#
#        self.update()
#
#    def update(self):
#        self.im.set_data(self.X[:,:,self.ind])
#        ax.set_ylabel('slice %s'%self.ind)
#        self.im.axes.figure.canvas.draw()
#
#
#fig = figure()
#ax = fig.add_subplot(111)
#
#X = numpy.random.rand(20,20,40)
#
#tracker = IndexTracker(ax, X)
#
#
#
#fig.canvas.mpl_connect('scroll_event', tracker.onscroll)
#show()
    