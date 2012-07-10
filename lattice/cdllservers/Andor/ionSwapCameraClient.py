import sys
from PyQt4 import QtGui, QtCore
from datavault import DataVaultWidget
from matplotlib.figure import Figure
from matplotlib import cm
import matplotlib.pyplot as plt
import time


from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread
from datetime import datetime

import matplotlib.pyplot as plt


import numpy as np

EMGAIN = 255
EXPOSURE = .1 #sec

class CameraCanvas(FigureCanvas):
    """Matplotlib Figure widget to display CPU utilization"""
    def __init__(self, parent):
        self.parent = parent
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
      
        
    def newAxes(self, data, hstart, hend, vstart, vend):
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)
        print hstart, hend, vstart, vend
        self.im = self.ax.imshow(data, extent=[hstart, hend, vstart, vend], origin='lower', interpolation='nearest')#, cmap=cm.hot)#gist_heat)


    def updateData(self, data, width, height):
        try:
            self.data = np.reshape(data, (height, width))
        except ValueError:
            pass # happens if update data is called before the new width and height are calculated upon changing the image size

        self.im.set_data(self.data)
        self.im.axes.figure.canvas.draw()
       
class HistCanvas(FigureCanvas):
    """Matplotlib Figure widget to display CPU utilization"""
    def __init__(self, parent, ionCatalogArray, ionSwapCatalog):
        self.parent = parent
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)

        self.ax1 = self.fig.add_subplot(141)
        self.ax2 = self.fig.add_subplot(142)
        self.ax3 = self.fig.add_subplot(143)
        self.ax4 = self.fig.add_subplot(144)
        
        self.setHist(self.ax1, ionCatalogArray[0], label = 'initial')
        self.setHist(self.ax2, ionCatalogArray[1], label = 'shine729')
        self.setHist(self.ax3, ionCatalogArray[2], label = 'final')
        
        self.ax1.set_xlabel('Number Of Bright Ions')
        self.ax1.set_ylim(0, 1)
        self.ax2.set_xlabel('Number Of Dark Ions')
        self.ax2.text(.35, .75, str((len(np.where(np.array(ionCatalogArray[1]) == 1)[0])/float(len(ionCatalogArray[1])))*100) + ' percent w/ one ion dark', fontsize=12, transform = self.ax2.transAxes)
        self.ax2.text(.35, .8, 'Mean: ' + str(np.mean(ionCatalogArray[1])) + ' ions dark', transform = self.ax2.transAxes)
        self.ax2.set_ylim(0, 1)
        self.ax3.set_xlabel('Number Of Dark Ions')
        self.ax3.text(.35, .75, str((len(np.where(np.array(ionCatalogArray[2]) == 1)[0])/float(len(ionCatalogArray[2])))*100) + ' percent w/ one ion dark', fontsize=12, transform = self.ax3.transAxes)
        self.ax3.text(.35, .8, 'Mean: ' + str(np.mean(ionCatalogArray[2])) + ' ions dark', transform = self.ax3.transAxes)
        self.ax3.set_ylim(0, 1)

        self.ax4.hist(ionSwapCatalog, bins=range(self.parent.parent.expectedNumberOfIonsSpinBox.value() + 1), align='left', normed = True, label = 'Ion Swaps' )
        self.ax4.legend(loc='best')
        self.ax4.set_xlabel('Distance of Ion Movement')
        self.ax4.text(.25, .8, 'Number Ion Swaps: ' + str(len(np.where(np.array(ionSwapCatalog) == 1)[0])), transform = self.ax4.transAxes)
        self.ax4.text(0.025, .75, '1 ion dark in both shine729 and final: ' + str(len(ionSwapCatalog)/float(len(ionCatalogArray[0]))*100) + ' %', transform = self.ax4.transAxes)
        self.ax4.text(0.10, .70, 'Probability of Ion Swap: ' + str(len(np.where(np.array(ionSwapCatalog) == 1)[0])/float(len(ionSwapCatalog))), transform = self.ax4.transAxes)

    def setHist(self, ax, data, label):
        ax.hist(data, bins=range(10), align='left', normed=True, label = label)
        ax.legend(loc='best')
        self.ax4.set_ylim(0, 1)
        
        
class HistWindow(QtGui.QWidget):        
    """Creates the window for the new plot"""
    def __init__(self, parent, ionCatalogArray, ionSwapCatalog):
        QtGui.QWidget.__init__(self)
        
        self.parent = parent
        
        layout = QtGui.QVBoxLayout()
        
        #try:
        canvas = HistCanvas(self, ionCatalogArray, ionSwapCatalog)
        #except AttributeError:
            #raise Exception("Has a Dark Ion Catalog Been Retrieved?")
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
        
       
        self.layout = QtGui.QVBoxLayout()
       
        
        temperatureButton = QtGui.QPushButton("Temp", self)
        temperatureButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        temperatureButton.clicked.connect(self.printTemperature)     
        
                     
        
#        openKineticButton = QtGui.QPushButton("Open Kinetic", self)
#        openKineticButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
#        openKineticButton.clicked.connect(self.openKinetic)

#        openKineticDataVaultButton = QtGui.QPushButton("Open Kinetic Data Vault", self)
#        openKineticDataVaultButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
#        openKineticDataVaultButton.clicked.connect(self.openKineticDataVault)
#        
#        saveKineticDataVaultButton = QtGui.QPushButton("Temp Save DV", self)
#        saveKineticDataVaultButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
#        saveKineticDataVaultButton.clicked.connect(self.saveKineticDataVault)        
        
        abortAcquisitionButton = QtGui.QPushButton("Abort Acquisition", self)
        abortAcquisitionButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        abortAcquisitionButton.clicked.connect(self.abortAcquisition)

        
        getIonNumberHistogramButton = QtGui.QPushButton("Ion Swap - Ion Number", self)
        getIonNumberHistogramButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        getIonNumberHistogramButton.clicked.connect(self.getIonNumberHistogram)
        
        loadDatasetsButton = QtGui.QPushButton("Load Datasets", self)
        loadDatasetsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        loadDatasetsButton.clicked.connect(self.loadDatasets)      
        
        
#        pathLabel = QtGui.QLabel()
#        pathLabel.setText('Path: ')
        
        pathDataVaultLabel = QtGui.QLabel()
        pathDataVaultLabel.setText('Path: ')        
        
#        self.pathEdit = QtGui.QLineEdit()
#        self.pathEdit.setText(r'C:\Users\lattice\Documents\Andor\jun12\062812\1\image') 
        
        self.pathDataVaultEdit = QtGui.QLineEdit()
        self.pathDataVaultEdit.setText(str(['','Experiments', 'IonSwap', '2012Jul09']))        

        self.loadDatasetsEdit = QtGui.QLineEdit()
        self.loadDatasetsEdit.setText(str([100031, 100035, 100039]))              
                        
#        exposureLabel = QtGui.QLabel()
#        exposureLabel.setText('Exposure (ms): ')

        iterationsLabel = QtGui.QLabel()
        iterationsLabel.setText('Iterations: ')
        
        ionThresholdLabel = QtGui.QLabel()
        ionThresholdLabel.setText('Ion Threshold: ')

        darkIonThresholdLabel = QtGui.QLabel()
        darkIonThresholdLabel.setText('Dark Ion Threshold: ')
        
        imageNumberLabel = QtGui.QLabel()
        imageNumberLabel.setText('Image Number: ')
        
        kineticSetsLabel = QtGui.QLabel()
        kineticSetsLabel.setText('Kinetic Sets: ')
        
        expectedNumberOfIonsLabel = QtGui.QLabel()
        expectedNumberOfIonsLabel.setText('Expected Number Of Ions: ') 
        
        alphaLabel = QtGui.QLabel()
        alphaLabel.setText('Alpha: ')
        
        axialOffsetLabel = QtGui.QLabel()
        axialOffsetLabel.setText('Axial Offset: ')

        sigmaLabel = QtGui.QLabel()
        sigmaLabel.setText('Sigma: ')
        
        loadDatasetsLabel = QtGui.QLabel()
        loadDatasetsLabel.setText('Datasets: ')                       
        
             
        
#        self.exposureSpinBox = QtGui.QSpinBox()
#        self.exposureSpinBox.setMinimum(100)
#        self.exposureSpinBox.setMaximum(1000)
#        self.exposureSpinBox.setSingleStep(1)  
#        self.exposureSpinBox.setValue(EXPOSURE*1000)     
#        self.exposureSpinBox.setKeyboardTracking(False)
#        self.connect(self.exposureSpinBox, QtCore.SIGNAL('valueChanged(int)'), self.changeExposure)

        self.iterationsSpinBox = QtGui.QSpinBox()
        self.iterationsSpinBox.setMinimum(0)
        self.iterationsSpinBox.setMaximum(1000)
        self.iterationsSpinBox.setSingleStep(1)  
        self.iterationsSpinBox.setValue(2)     
        self.iterationsSpinBox.setKeyboardTracking(False)

        self.kineticSetsSpinBox = QtGui.QSpinBox()
        self.kineticSetsSpinBox.setMinimum(0)
        self.kineticSetsSpinBox.setMaximum(100)
        self.kineticSetsSpinBox.setSingleStep(1)  
        self.kineticSetsSpinBox.setValue(3)     
        self.kineticSetsSpinBox.setKeyboardTracking(False)


        self.ionThresholdSpinBox = QtGui.QSpinBox()
        self.ionThresholdSpinBox.setMinimum(0)
        self.ionThresholdSpinBox.setMaximum(1000)
        self.ionThresholdSpinBox.setSingleStep(1)  
        self.ionThresholdSpinBox.setValue(700)     
        self.ionThresholdSpinBox.setKeyboardTracking(False)

        self.darkIonThresholdSpinBox = QtGui.QSpinBox()
        self.darkIonThresholdSpinBox.setMinimum(-1000)
        self.darkIonThresholdSpinBox.setMaximum(0)
        self.darkIonThresholdSpinBox.setSingleStep(1)  
        self.darkIonThresholdSpinBox.setValue(-350)     
        self.darkIonThresholdSpinBox.setKeyboardTracking(False)
        
        self.alphaSpinBox = QtGui.QSpinBox()
        self.alphaSpinBox.setMinimum(1)
        self.alphaSpinBox.setMaximum(50)
        self.alphaSpinBox.setSingleStep(1)  
        self.alphaSpinBox.setValue(15)     
        self.alphaSpinBox.setKeyboardTracking(False)

        self.axialOffsetSpinBox = QtGui.QSpinBox()
        self.axialOffsetSpinBox.setMinimum(1)
        self.axialOffsetSpinBox.setMaximum(100)
        self.axialOffsetSpinBox.setSingleStep(1)  
        self.axialOffsetSpinBox.setValue(33)     
        self.axialOffsetSpinBox.setKeyboardTracking(False)

        self.sigmaSpinBox = QtGui.QSpinBox()
        self.sigmaSpinBox.setMinimum(1)
        self.sigmaSpinBox.setMaximum(50)
        self.sigmaSpinBox.setSingleStep(1)  
        self.sigmaSpinBox.setValue(5)     
        self.sigmaSpinBox.setKeyboardTracking(False)        
        
        self.expectedNumberOfIonsSpinBox = QtGui.QSpinBox()
        self.expectedNumberOfIonsSpinBox.setMinimum(1)
        self.expectedNumberOfIonsSpinBox.setMaximum(10)
        self.expectedNumberOfIonsSpinBox.setSingleStep(1)  
        self.expectedNumberOfIonsSpinBox.setValue(5)     
        self.expectedNumberOfIonsSpinBox.setKeyboardTracking(False)               
        
        imageAnalyzedLabel = QtGui.QLabel()
        imageAnalyzedLabel.setText('Images to analyze: ')

        typIonDiameterLabel = QtGui.QLabel()
        typIonDiameterLabel.setText('Typical Ion Diameter: ')
        
#        peakVicinityLabel = QtGui.QLabel()
#        peakVicinityLabel.setText('Peak Vicinity: ')
        
        
        self.imageAnalyzedSpinBox = QtGui.QSpinBox()
        self.imageAnalyzedSpinBox.setMinimum(1)
        self.imageAnalyzedSpinBox.setMaximum(20)
        self.imageAnalyzedSpinBox.setSingleStep(1)  
        self.imageAnalyzedSpinBox.setValue(2)     
        self.imageAnalyzedSpinBox.setKeyboardTracking(False)        

        self.typIonDiameterSpinBox = QtGui.QSpinBox()
        self.typIonDiameterSpinBox.setMinimum(1)
        self.typIonDiameterSpinBox.setMaximum(20)
        self.typIonDiameterSpinBox.setSingleStep(1)  
        self.typIonDiameterSpinBox.setValue(5)     
        self.typIonDiameterSpinBox.setKeyboardTracking(False) 
          
          
         # Layout
        self.bottomPanel1 = QtGui.QHBoxLayout()
        
        self.bottomPanel1.addWidget(temperatureButton)
        self.bottomPanel1.addWidget(getIonNumberHistogramButton)
        self.bottomPanel1.addWidget(kineticSetsLabel)
        self.bottomPanel1.addWidget(self.kineticSetsSpinBox)
    
        self.bottomPanel1.addStretch(0)
        self.bottomPanel1.setSizeConstraint(QtGui.QLayout.SetFixedSize)        
        self.bottomPanel1.addWidget(iterationsLabel)
        self.bottomPanel1.addWidget(self.iterationsSpinBox)
        self.bottomPanel1.addWidget(alphaLabel)
        self.bottomPanel1.addWidget(self.alphaSpinBox)
        self.bottomPanel1.addWidget(axialOffsetLabel)
        self.bottomPanel1.addWidget(self.axialOffsetSpinBox)
        self.bottomPanel1.addWidget(sigmaLabel)
        self.bottomPanel1.addWidget(self.sigmaSpinBox)
        
        self.bottomPanel2 = QtGui.QHBoxLayout()

#        self.bottomPanel2.addStretch(0)

        self.bottomPanel2.addWidget(abortAcquisitionButton)
        self.bottomPanel2.addWidget(imageAnalyzedLabel)
        self.bottomPanel2.addWidget(self.imageAnalyzedSpinBox)
        self.bottomPanel2.addWidget(expectedNumberOfIonsLabel)
        self.bottomPanel2.addWidget(self.expectedNumberOfIonsSpinBox)
        self.bottomPanel2.addWidget(typIonDiameterLabel)
        self.bottomPanel2.addWidget(self.typIonDiameterSpinBox)

        
#        self.bottomPanel3 = QtGui.QHBoxLayout()
#
#
#        self.bottomPanel3.addWidget(openKineticButton)
#        self.bottomPanel3.addWidget(pathLabel)
#        self.bottomPanel3.addWidget(self.pathEdit)
        
#        self.bottomPanel4 = QtGui.QHBoxLayout()

#        self.bottomPanel4.addWidget(saveKineticDataVaultButton)
#        self.bottomPanel4.addWidget(openKineticDataVaultButton)
#        self.bottomPanel4.addWidget(pathDataVaultLabel)
#        self.bottomPanel4.addWidget(self.pathDataVaultEdit)        
        
        self.bottomPanel3 = QtGui.QHBoxLayout()

        self.bottomPanel3.addWidget(loadDatasetsButton)
        self.bottomPanel3.addWidget(loadDatasetsLabel)
        self.bottomPanel3.addWidget(self.loadDatasetsEdit)
        self.bottomPanel3.addWidget(pathDataVaultLabel)
        self.bottomPanel3.addWidget(self.pathDataVaultEdit)    
        
        
        self.layout.addLayout(self.bottomPanel1)
        self.layout.addLayout(self.bottomPanel2)
        self.layout.addLayout(self.bottomPanel3)

        self.setWindowTitle('Dark Ion Analysis')  
        self.setLayout(self.layout)
        
        self.setupViewingTools()       


    @inlineCallbacks
    def setupViewingTools(self):    
        context = yield self.parent.cxn.context()
        self.datavaultwidget = DataVaultWidget(self, context)
        self.datavaultwidget.populateList()     
        self.bottomPanel4 = QtGui.QHBoxLayout()
        self.bottomPanel4.addWidget(self.datavaultwidget)
        self.layout.addLayout(self.bottomPanel4)
              
        cameraCanvasLayout = QtGui.QVBoxLayout()
        
        self.bottomPanel4.addLayout(cameraCanvasLayout)
        
        self.cameraCanvas = CameraCanvas(self)
        self.cameraCanvas.show()
        ntb = NavigationToolbar(self.cameraCanvas, self)

        cameraCanvasLayout.addWidget(self.cameraCanvas)
        cameraCanvasLayout.addWidget(ntb)
        


    def printTemperature(self, evt):
        self.parent.printTemperature()
    
    def getDarkIonCatalog(self, evt):
        self.parent.getDarkIonCatalog(self.imageAnalyzedSpinBox.value(), self.typIonDiameterSpinBox.value(), self.ionThresholdSpinBox.value(), self.darkIonThresholdSpinBox.value(), self.iterationsSpinBox.value())
        
    def getIonPositionCatalog(self, evt):
        self.parent.getIonPositionCatalog(self.imageAnalyzedSpinBox.value(), self.typIonDiameterSpinBox.value(), self.ionThresholdSpinBox.value(), self.darkIonThresholdSpinBox.value(), self.iterationsSpinBox.value(), self.peakVicinitySpinBox.value())
    
    def collectData(self, evt):
        self.parent.collectData(self.iterationsSpinBox.value(), self.imageAnalyzedSpinBox.value())
    
#    def changeExposure(self, value):
#        self.parent.changeExposure(float(self.exposureSpinBox.value())/1000) #convert ms to s     
#        
#    def countDarkIons(self, evt):
#        histWindow = HistWindow(self, self.parent.darkIonCatalog)
#        self.histList.append(histWindow)
#        histWindow.show()
#        print np.mean(self.parent.darkIonCatalog)
        
    @inlineCallbacks
    def getIonNumberHistogram(self, evt):
        ionNumberCatalogArray = []
        yield self.parent.buildDarkIonPositionCatalog(self.kineticSetsSpinBox.value(), self.imageAnalyzedSpinBox.value(), self.typIonDiameterSpinBox.value(), self.expectedNumberOfIonsSpinBox.value(), self.iterationsSpinBox.value(), [self.alphaSpinBox.value(), self.axialOffsetSpinBox.value(), self.sigmaSpinBox.value()])
        for i in range(3): 
            ionNumberCatalog = yield self.parent.getIonNumberHistogram(i + 1, self.imageAnalyzedSpinBox.value(), self.iterationsSpinBox.value(), self.kineticSetsSpinBox.value())
            ionNumberCatalogArray.append(ionNumberCatalog)
        ionSwapCatalog = yield self.parent.getIonSwapHistogram(self.imageAnalyzedSpinBox.value(), self.iterationsSpinBox.value(), self.expectedNumberOfIonsSpinBox.value(), self.kineticSetsSpinBox.value())
        histWindow = HistWindow(self, ionNumberCatalogArray, ionSwapCatalog)
        self.histList.append(histWindow)
        histWindow.show()
    
    def openKinetic(self, evt):
        self.parent.openKinetic(str(self.pathEdit.text()), self.kineticSetsSpinBox.value(), ((self.imageAnalyzedSpinBox.value() + 1)*self.iterationsSpinBox.value()))
        
    def openKineticDataVault(self, evt):
        self.parent.openKineticDataVault(str(self.pathDataVaultEdit.text()), ((self.imageAnalyzedSpinBox.value() + 1)*self.iterationsSpinBox.value()))

    def loadDatasets(self, evt):
        self.parent.loadDatasets(str(self.pathDataVaultEdit.text()), str(self.loadDatasetsEdit.text()), ((self.imageAnalyzedSpinBox.value() + 1)*self.iterationsSpinBox.value()))
    
    def saveKineticDataVault(self, evt):
        self.parent.saveKineticDataVault(str(self.pathDataVaultEdit.text()), 'image', ((self.imageAnalyzedSpinBox.value() + 1)*self.iterationsSpinBox.value()))

    def abortAcquisition(self, evt):
        self.parent.abortAcquisition()
    
    def getData(self, evt):
        self.parent.getData(((self.imageAnalyzedSpinBox.value() + 1)*self.iterationsSpinBox.value()))

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
            yield self.server.set_trigger_mode(1)
        except:
            print 'client not closed properly'
            self.abortAcquisition()
            yield self.server.set_trigger_mode(1)
        yield self.server.set_read_mode(4)
        yield self.server.set_emccd_gain(EMGAIN)
        yield self.server.set_exposure_time(EXPOSURE)   
        yield self.server.cooler_on()
        
        
        #self.detectorDimensions = yield self.server.get_detector_dimensions() #this gives a type error?
        
        self.hstart = 455
        self.hend = 530
        self.vstart = 217
        self.vend = 242
        
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
              
#    @inlineCallbacks
#    def openKinetic(self, path, kinSet, numKin):
#        yield self.server.open_as_text_kinetic(path, kinSet, numKin)
#        print 'opened!'

#    @inlineCallbacks
#    def openKineticDataVault(self, path, numKin):
#        yield self.server.open_from_data_vault_kinetic(path, numKin)
#        print 'opened!'        

    @inlineCallbacks
    def loadDatasets(self, path, datasets, numKin):
        yield self.server.clear_image_array()
        datasets = [str(tuple(eval(path))[-1]) + '_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in tuple(eval(datasets))]
        print datasets
        for dataset in datasets:
            datasetPath = str(path[0:-1] + ', ' + '\'' + dataset + '\', \'Scans\']'  )
            print datasetPath
            yield self.server.open_from_data_vault_kinetic(datasetPath, numKin)

#    @inlineCallbacks
#    def saveKineticDataVault(self, path, name, numKin):
#        yield self.server.save_to_data_vault_kinetic(path, name, numKin)
#        print 'saved!'        
    
    @inlineCallbacks
    def buildDarkIonPositionCatalog(self, kinSet, numAnalyzedImages, typicalIonDiameter, expectedNumberOfIons, iterations, initialParameters):
        numKin =  (numAnalyzedImages + 1)*iterations
        yield self.server.build_dark_ion_position_catalog(kinSet, numKin, (self.height + 1), (self.width + 1), typicalIonDiameter, expectedNumberOfIons, iterations, initialParameters)
        
    @inlineCallbacks
    def getIonNumberHistogram(self, imageNumber, numAnalyzedImages, iterations, kinSet):
        numKin =  (numAnalyzedImages + 1)*iterations
        ionNumberCatalog = yield self.server.get_ion_number_histogram(imageNumber, kinSet, numKin, iterations)
        print ionNumberCatalog
        returnValue(ionNumberCatalog)
    
    @inlineCallbacks
    def getIonSwapHistogram(self, numAnalyzedImages, iterations, expectedNumberOfIons, kinSet):
        numKin =  (numAnalyzedImages + 1)*iterations
        ionSwapCatalog = yield self.server.get_ion_swap_histogram(iterations, kinSet, numKin, expectedNumberOfIons)
        print ionSwapCatalog
        returnValue(ionSwapCatalog)
        
    
    @inlineCallbacks
    def abortAcquisition(self):
        yield self.server.abort_acquisition()
        print 'aborted'
               
if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    ionCount = IonCount(reactor)
    reactor.run()
    
