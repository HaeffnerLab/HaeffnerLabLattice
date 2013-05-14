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
        FigureCanvas.__init__(self, self.fig)
#        hstart = self.parent.parent.hstart
#        hend = self.parent.parent.hend
#        vstart = self.parent.parent.vstart
#        vend = self.parent.parent.vend
#
#        width = hend - hstart
#        height = vend - vstart

        #dummy data for now
        #blankData = np.zeros(width*height)
        #self.data = np.reshape(blankData, (height, width))
        #self.newAxes(hstart, hend, vstart, vend)

        self.cnt = 0
        
        
    def newAxes(self, hstart, hend, vstart, vend):
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)
        print hstart, hend, vstart, vend
        self.im = self.ax.imshow(self.data, extent=[hstart, hend, vstart, vend], origin='lower', interpolation='nearest')#, cmap=cm.hot)#gist_heat)
        self.setupSelector()


    def updateData(self, data, width, height):
        try:
            self.data = np.reshape(data, (height, width))
        except ValueError:
            pass # happens if update data is called before the new width and height are calculated upon changing the image size

        self.im.set_data(self.data)
        self.im.axes.figure.canvas.draw()


#        try: 
#            self.im.set_data(self.data)
#            self.im.axes.figure.canvas.draw()
#        except:
#            print self.data.shape
#            self.im = self.ax.matshow(self.data)#, extent=[self.parent.parent.hstart, self.parent.parent.hend, self.parent.parent.vstart, self.parent.parent.vend])#, cmap=cm.hot)#gist_heat)
#            #self.ax.axis([self.parent.parent.hstart, self.parent.parent.hend, self.parent.parent.vstart, self.parent.parent.vend])
#            self.im.axes.figure.canvas.draw()
    
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
        #self.ax.axis([int(eclick.xdata), int(erelease.xdata), int(eclick.ydata), int(erelease.ydata)])
        #self.ax.set_xlim(int(eclick.xdata), int(erelease.xdata))
        #self.ax.set_ylim(int(eclick.ydata), int(erelease.ydata))

    
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
        
        kineticButton = QtGui.QPushButton("Kinetic", self)
        kineticButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        kineticButton.clicked.connect(self.kineticScan)
        
        saveKineticButton = QtGui.QPushButton("Save Kinetic", self)
        saveKineticButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        saveKineticButton.clicked.connect(self.saveKinetic)
    
        openKineticButton = QtGui.QPushButton("Open Kinetic", self)
        openKineticButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        openKineticButton.clicked.connect(self.openKinetic)   
        
        numKineticLabel = QtGui.QLabel()
        numKineticLabel.setText('Number of Scans: ')
                
        self.numKineticSpinBox = QtGui.QSpinBox()
        self.numKineticSpinBox.setMinimum(0)
        self.numKineticSpinBox.setMaximum(1000)
        self.numKineticSpinBox.setSingleStep(1)  
        self.numKineticSpinBox.setValue(10)     
        self.numKineticSpinBox.setKeyboardTracking(False) 
        
        kineticCycleTimeLabel = QtGui.QLabel()
        kineticCycleTimeLabel.setText('Kinetic Cycle Time (ms): ')
                
        self.kineticCycleTimeSpinBox = QtGui.QSpinBox()
        self.kineticCycleTimeSpinBox.setMinimum(0)
        self.kineticCycleTimeSpinBox.setMaximum(1000)
        self.kineticCycleTimeSpinBox.setSingleStep(1)  
        self.kineticCycleTimeSpinBox.setValue(10)     
        self.kineticCycleTimeSpinBox.setKeyboardTracking(False)        
        
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
        self.exposureSpinBox.setMinimum(100)
        self.exposureSpinBox.setMaximum(1000)
        self.exposureSpinBox.setSingleStep(1)  
        self.exposureSpinBox.setValue(EXPOSURE*1000)     
        self.exposureSpinBox.setKeyboardTracking(False)
        self.connect(self.exposureSpinBox, QtCore.SIGNAL('valueChanged(int)'), self.changeExposure)

        
         # Layout
        self.bottomPanel1 = QtGui.QHBoxLayout()
        
        self.bottomPanel1.addWidget(temperatureButton)
        self.bottomPanel1.addWidget(liveVideoButton)
        self.bottomPanel1.addWidget(abortButton)
        self.bottomPanel1.addWidget(resetScaleButton)
        self.bottomPanel1.addWidget(singleButton)
        self.bottomPanel1.addWidget(emGainLabel)
        self.bottomPanel1.addWidget(self.emGainSpinBox)
        self.bottomPanel1.addWidget(exposureLabel)
        self.bottomPanel1.addWidget(self.exposureSpinBox)
    
        self.bottomPanel1.addStretch(0)
        self.bottomPanel1.setSizeConstraint(QtGui.QLayout.SetFixedSize)        
        layout.addLayout(self.bottomPanel1)
        
        self.bottomPanel2 = QtGui.QHBoxLayout()
        
        self.bottomPanel2.addWidget(kineticButton)
        self.bottomPanel2.addWidget(numKineticLabel)
        self.bottomPanel2.addWidget(self.numKineticSpinBox)
        self.bottomPanel2.addWidget(kineticCycleTimeLabel)
        self.bottomPanel2.addWidget(self.kineticCycleTimeSpinBox)
        self.bottomPanel2.addWidget(saveKineticButton)
        self.bottomPanel2.addWidget(openKineticButton)
            
        self.bottomPanel2.addStretch(0)
        self.bottomPanel2.setSizeConstraint(QtGui.QLayout.SetFixedSize)        
        layout.addLayout(self.bottomPanel2)
        
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
    
    def kineticScan(self, evt):
        self.parent.kineticScan(self.numKineticSpinBox.value(),(self.kineticCycleTimeSpinBox.value()/1000.0))    
    
    def liveVideo(self, evt):
        self.parent.liveVideo()
        
    def resetScale(self, evt):
        self.parent.changeImageRegion(self.parent.originalHStart,self.parent.originalVStart,self.parent.originalHEnd,self.parent.originalVEnd)
        
    def saveKinetic(self, evt):
        self.parent.saveKinetic(self.numKineticSpinBox.value())
    
    def openKinetic(self, evt):
        self.parent.openKinetic(self.numKineticSpinBox.value())
    
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
            self.setupListeners()
            self.setupCamera()
        except Exception ,e:
            print 'server not connected: {}'.format(e)

    @inlineCallbacks
    def setupListeners(self):
#        yield self.server.signal__kinetic_finish(88888)
#        yield self.server.addListener(listener = self.kineticFinish, source = None, ID = 88888)
        yield self.server.signal__acquisition_event(99999)
        yield self.server.addListener(listener = self.acquisitionEvent, source = None, ID = 99999)
        
    
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
        
        self.openVideoWindow()

        
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

        t1 = time.clock() 
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
        for i in height:
            Height.append([i]*lenWidth)
        Height = np.ravel(np.array(Height))
        
        yield self.cxn.data_vault.cd('Camera Snapshots')
        t = datetime.now()
        dateTime = str(t.strftime("%Y-%m-%d %H:%M:%S"))
#        yield self.cxn.data_vault.new('Half-Life', [('x', 'in')], [('y','','in')])         
#        yield self.cxn.data_vault.add([[0.0,0.2],[1.0,0.2],[2.4,2.3],[3.3,0.0],[4.7,0.4],[4.5,1.2],[3.8,1.0],[2.3,4.8],[1.1,4.8],[1.1,4.1],[1.7,4.1],[2.0,3.4],[0.0,0.2]] )
        yield self.cxn.data_vault.new(dateTime, [('Pixels', '')], [('Pixels','',''), ('Counts','','')])         
        toDataVault = np.array(np.vstack((Height, Width, self.newdata)).transpose(), dtype=float)
        print toDataVault
        yield self.cxn.data_vault.add(toDataVault)
        t2 = time.clock()
        print 'time for an image of size : ', (self.width + 1), (self.height + 1), (t2-t1), ' sec'
        print 'saved!'
#            newarray = np.reshape(newdata, (height, width))
#            ax.matshow(newarray)
#                
#        fig.show()

    @inlineCallbacks
    def kineticScan(self, numKin, cycTime):
        status = yield self.server.get_status()
        if (status == 'DRV_IDLE'):
            print numKin
            self.numKin = numKin
            yield self.server.set_acquisition_mode(3)
            yield self.server.set_number_kinetics(numKin)
            yield self.server.set_kinetic_cycle_time(cycTime)
                
            print "Ready for Acquisition..."
            
            yield self.server.start_acquisition_kinetic(numKin)
            print 'acquired?'
            yield self.server.get_acquired_data_kinetic(self.numKin)

            
#    @inlineCallbacks 
#    def kineticFinish(self,x,y): 
#        data = yield self.server.get_acquired_data_kinetic(self.numKin)
#        newdata = data.asarray
#        
#        print newdata[12:14]
#            
            
    def acquisitionEvent(self, x, y):
        print y
    
  
    @inlineCallbacks
    def liveVideo(self):
               
        width = self.width
        height = self.height
        
        print "Ready for Acquisition..."
        
        status = yield self.server.get_status()
        if (status == 'DRV_IDLE'):
            yield self.server.set_acquisition_mode(5)
            yield self.server.start_acquisition()
            try:
                self.win.cmon.newAxes(self.hstart, self.hend, self.vstart, self.vend)
            except AttributeError:
                print 'yup outside the while'                    
            cnt = 0
            self.live = True
            while(self.live == True):
                data = yield self.server.get_most_recent_image()
                self.newdata = data.asarray
                try:
                    self.win.cmon.updateData(self.newdata, (width + 1), (height + 1))
                except AttributeError:
                    print 'yup in the while'
                    self.win.cmon.newAxes(self.hstart, self.hend, self.vstart, self.vend)
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
        #self.win.cmon.newAxes(self.hstart, self.hend, self.vstart, self.vend)
    
    @inlineCallbacks
    def saveKinetic(self, numKin):
        path = 'image'
        yield self.server.save_as_text_kinetic(path, numKin)
        print 'saved!'
    
    @inlineCallbacks
    def openKinetic(self, numKin):
        path = 'image'
        yield self.server.open_as_text_kinetic(path, numKin)
        print 'opened!'
        
        
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
    