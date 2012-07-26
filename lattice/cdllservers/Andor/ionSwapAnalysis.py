import sys
from PyQt4 import QtGui, QtCore
from datavault import DataVaultWidget
from matplotlib.figure import Figure
from matplotlib import cm
import matplotlib.pyplot as plt
import time
from scipy import ndimage
from scipy import optimize
from scipy.stats import chisquare
from itertools import product
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

HSTART = 455
HEND   = 530
VSTART = 217
VEND   = 242

#EMGAIN = 255
#EXPOSURE = .1 #sec

class AnalysisCanvas(FigureCanvas):
    """Matplotlib Figure widget to display CPU utilization"""
    def __init__(self, parent):
        self.parent = parent
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
      
        
        self.ax = self.fig.add_subplot(111)
        
    def drawPlot(self, dataset, directory, x, y1, y2 = None, parametersArray = None, arrangement = None, analysisTime = None):
        self.ax.cla()
        self.ax.plot(x, y1, label = 'Axial Sums')
        if (y2 != None):
            self.ax.plot(x, y2, label = 'Model')
        if ((arrangement != None) and (analysisTime != None)):
            self.ax.set_title('Dataset: ' + str(dataset) + ' - ' + str(directory) + ' - ' + str(arrangement) + ' - ' + str(analysisTime[0:8]))
        else:
            self.ax.set_title('Dataset: ' + str(dataset) + ' - ' + str(directory))
        self.ax.legend(loc='best')
        self.draw()
        #plot stuff!

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
       
        
#        temperatureButton = QtGui.QPushButton("Temp", self)
#        temperatureButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
#        temperatureButton.clicked.connect(self.printTemperature)     
        
                     
        
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
        
#        abortAcquisitionButton = QtGui.QPushButton("Abort Acquisition", self)
#        abortAcquisitionButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
#        abortAcquisitionButton.clicked.connect(self.abortAcquisition)

        
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
        self.pathDataVaultEdit.setText(str(['','Experiments', 'IonSwap', '2012Jun28']))        

        self.loadDatasetsEdit = QtGui.QLineEdit()
        self.loadDatasetsEdit.setText(str([111111]))              
                        
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
        self.iterationsSpinBox.setValue(50)     
        self.iterationsSpinBox.setKeyboardTracking(False)

        self.kineticSetsSpinBox = QtGui.QSpinBox()
        self.kineticSetsSpinBox.setMinimum(0)
        self.kineticSetsSpinBox.setMaximum(100)
        self.kineticSetsSpinBox.setSingleStep(1)  
        self.kineticSetsSpinBox.setValue(1)     
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
        
#        self.bottomPanel1.addWidget(temperatureButton)
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

#        self.bottomPanel2.addWidget(abortAcquisitionButton)
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
        ntbCamera = NavigationToolbar(self.cameraCanvas, self)

        cameraCanvasLayout.addWidget(self.cameraCanvas)
        cameraCanvasLayout.addWidget(ntbCamera)
        
        analysisCanvasLayout = QtGui.QVBoxLayout()
        
        self.bottomPanel4.addLayout(analysisCanvasLayout)
        
        self.analysisCanvas = AnalysisCanvas(self)
        self.analysisCanvas.show()
        ntbAnalysis = NavigationToolbar(self.analysisCanvas, self)

        analysisCanvasLayout.addWidget(self.analysisCanvas)
        self.parametersEdit = QtGui.QLineEdit(readOnly=True)
        analysisCanvasLayout.addWidget(self.parametersEdit)
        analysisCanvasLayout.addWidget(ntbAnalysis)
        
    def setParametersText(self, parametersArray):
        self.parametersEdit.setText('Height: ' + str(parametersArray[0]) + ' ' + 'Alpha: ' + str(parametersArray[1]) + ' ' + 'AxialOffset: ' + str(parametersArray[2]) + ' ' + 'Sigma: ' + str(parametersArray[3]) + ' ' + 'Offset: ' + str(parametersArray[4]))       
        
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
        
    def getIonNumberHistogram(self, evt):
        ionNumberCatalogArray = []
        self.parent.buildDarkIonPositionCatalog(self.kineticSetsSpinBox.value(), self.imageAnalyzedSpinBox.value(), self.typIonDiameterSpinBox.value(), self.expectedNumberOfIonsSpinBox.value(), self.iterationsSpinBox.value(), [self.alphaSpinBox.value(), self.axialOffsetSpinBox.value(), self.sigmaSpinBox.value()])
        for i in range(3): 
            ionNumberCatalog = self.parent.getIonNumberHistogram(i + 1, self.imageAnalyzedSpinBox.value(), self.iterationsSpinBox.value(), self.kineticSetsSpinBox.value())
            ionNumberCatalogArray.append(ionNumberCatalog)
        ionSwapCatalog = self.parent.getIonSwapHistogram(self.imageAnalyzedSpinBox.value(), self.iterationsSpinBox.value(), self.expectedNumberOfIonsSpinBox.value(), self.kineticSetsSpinBox.value())
        histWindow = HistWindow(self, ionNumberCatalogArray, ionSwapCatalog)
        self.histList.append(histWindow)
        histWindow.show()
        self.parent.appendParametersToDatasets(self.imageAnalyzedSpinBox.value(), self.iterationsSpinBox.value(), self.kineticSetsSpinBox.value())
    
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
        self.positionDict = {
                            '2':                                  [-.62996, .62996],
                            '3':                                 [-1.0772, 0, 1.0772],
                            '4':                          [-1.4368, -.45438, .45438, 1.4368],
                            '5':                         [-1.7429, -0.8221, 0, 0.8221, 1.7429],
                            '6':                  [-2.0123, -1.4129, -.36992, .36992, 1.4129, 2.0123],
                            '7':                 [-2.2545, -1.1429, -.68694, 0, .68694, 1.1429, 2.2545],
                            '8':           [-2.4758, -1.6621, -.96701, -.31802, .31802, .96701, 1.6621, 2.4758],
                            '9':         [-2.6803, -1.8897, -1.2195, -.59958, 0, .59958, 1.2195, 1.8897, 2.6803],
                            '10': [-2.8708, -2.10003, -1.4504, -.85378, -.2821, .2821, .85378, 1.4504, 2.10003, 2.8708]
                            }        
        
        self.directoryList = []
        self.imageArray = []
        
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
            self.server = yield self.cxn.data_vault
            self.setupCamera()
        except Exception ,e:
            print 'server not connected: {}'.format(e)
   
    def setupCamera(self):
#        temp = yield self.server.get_current_temperature()
#        print temp
        
#        try:
#            yield self.server.set_trigger_mode(1)
#        except:
#            print 'client not closed properly'
#            self.abortAcquisition()
#            yield self.server.set_trigger_mode(1)
#        yield self.server.set_read_mode(4)
#        yield self.server.set_emccd_gain(EMGAIN)
#        yield self.server.set_exposure_time(EXPOSURE)   
#        yield self.server.cooler_on()
        
        
        #self.detectorDimensions = yield self.server.get_detector_dimensions() #this gives a type error?
        
        self.hstart = HSTART
        self.hend =  HEND
        self.vstart = VSTART
        self.vend = VEND
        
        self.width = self.hend - self.hstart
        self.height = self.vend - self.vstart
        
        print 'width: ', self.width
        print 'height: ', self.height
        
#        error = yield self.server.set_image_region(1,1,self.hstart,self.hend,self.vstart,self.vend)
#        print 'image: ', error
        
        self.openVideoWindow()




        
#    @inlineCallbacks
#    def printTemperature(self):
#        temp = yield self.server.get_current_temperature()
#        print temp
              
#    @inlineCallbacks
#    def openKinetic(self, path, kinSet, numKin):
#        yield self.server.open_as_text_kinetic(path, kinSet, numKin)
#        print 'opened!'

#    @inlineCallbacks
#    def openKineticDataVault(self, path, numKin):
#        yield self.server.open_from_data_vault_kinetic(path, numKin)
#        print 'opened!' 


################################ MAKE FUNCTIONS NATIVE!!!       

    def loadDatasets(self, path, datasets, numKin):
        self.imageArray = []
        datasets = [str(list(eval(path))[-1]) + '_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in list(eval(datasets))]
        print datasets
        self.directoryList = []
        for dataset in datasets:
            datasetPath = str(path[0:-1] + ', ' + '\'' + dataset + '\', \'Scans\']'  )
            print datasetPath
            self.directoryList.append(list(eval(datasetPath)))
            self.openFromDataVaultKinetic(list(eval(datasetPath)), numKin)   
    
    def buildDarkIonPositionCatalog(self, kinSet, numAnalyzedImages, typicalIonDiameter, expectedNumberOfIons, iterations, initialParameters):
        numKin =  (numAnalyzedImages + 1)*iterations
        self.darkIonPositionCatalog = self._buildDarkIonPositionCatalog(kinSet, numKin, (self.height + 1), (self.width + 1), typicalIonDiameter, expectedNumberOfIons, iterations, initialParameters)
        
    def appendParametersToDatasets(self, numAnalyzedImages, iterations, kinSet):
        numKin =  (numAnalyzedImages + 1)*iterations
        self._appendParametersToDatasets(kinSet, numKin, iterations)
        
    def getIonNumberHistogram(self, imageNumber, numAnalyzedImages, iterations, kinSet):
        numKin = (numAnalyzedImages + 1)*iterations
        self.ionNumberCatalog = self._getIonNumberCatalog(imageNumber, self.darkIonPositionCatalog, iterations, kinSet, numKin)
        print self.ionNumberCatalog
        return self.ionNumberCatalog
    
    def getIonSwapHistogram(self, numAnalyzedImages, iterations, expectedNumberOfIons, kinSet):
        numKin =  (numAnalyzedImages + 1)*iterations
        ionSwapCatalog = self._buildIonSwapCatalog(self.darkIonPositionCatalog, kinSet, iterations, expectedNumberOfIons)
        if (len(ionSwapCatalog) != 0):
            return np.array(ionSwapCatalog)
        else:
            return [-1]*len(self.ionNumberCatalog) #this means no ions at all
         
#    @inlineCallbacks
#    def abortAcquisition(self):
#        yield self.server.abort_acquisition()
#        print 'aborted'
               
               
######################## NEW FUNCTIONS

    @inlineCallbacks
    def openFromDataVaultKinetic(self, directory, numKin):
        dv = self.server
        yield dv.cd(directory)
        
        # use the first image to set dimensions
        yield dv.open(1)
        try: 
            hstart = yield dv.get_parameter('hstart')
            hend = yield dv.get_parameter('hend')
            vstart = yield dv.get_parameter('vstart')
            vend = yield dv.get_parameter('vend')
            
            print 'Border: ', hstart, hend, vstart, vend

            self.width = hend - hstart
            self.height = vend - vstart

        except:
            raise Exception('Does this scan have dimension parameters?')
        
        for i in np.arange(numKin):
            yield dv.open(int(i+1))
            Data = yield dv.get()
            data = Data.asarray
#            print data
            print 'lendata: ', len(data), (i+1)
            zData = np.array([None]*len(data))
            for j in np.arange(len(data)):
                zData[j] = data[j][2]
                
            self.imageArray.append(zData)
            print 'done!'            

    def _buildDarkIonPositionCatalog(self, kinSet, numKin, rows, cols, typicalIonDiameter, expectedNumberOfIons, iterations, initialParameters):
        
        """parametersArray = [height, alpha, axialOffset, sigma, offset], returned from _fitInitialImageData, used for each set of images (iteration)
       
        darkIonPositionCatalog is a list of lists of lists of lists of ion positions in the chain
                                     ^        ^        ^        ^
                                     |        |        |        |
                                 catalog    kinSet  iteration  image = dark ion positions

        
        Ex:    (5 ions)
        
            darkIonPositionCatalog[1st kinetic set][1st iteration][1st image] =    [5] --> means there are 5 bright ions (The first image in each set is the number of bright ions)
            darkIonPositionCatalog[1st kinetic set][1st iteration][2nd image] =    [1, 2] --> means two dark ions at positions 1 and 2 in the ion chain
            
                                                                                    ^
                                                                                    | --> dark ion position in [0, 1, 2, 3, 4]
                                                                            
            
        Note: len(darkIonPositionCatalog[0][1]) = number of dark ions for the first image to be analyzed
        
        """        
        
        try:
            data = np.reshape(np.array(self.imageArray, dtype=np.float), (kinSet, numKin, rows, cols))
        except ValueError:
            raise Exception("Trying to analyze more images than there is in the data? Image region correct?")
        
        numberImagesInSet = (numKin / iterations) # better equal 2 for ionSwap

        darkIonPositionCatalog = [[[] for i in range(iterations)] for j in range(kinSet)]

        xmodel = np.arange(cols, dtype=float)

        t1 = time.clock()
        
        self.kinSetParametersArray = [[] for i in range(kinSet*iterations)] # in order of image Sets in order of kinSet EXPLAIN ME BETTER LATER
        self.bestModelFits = [[] for i in range(kinSet)] #in order of images analyzed in order of kinSet EXPLAIN ME BETTER LATER
        self.analysisTimes = [[] for i in range(kinSet)] #in order of images analyzed in order of kinSet EXPLAIN ME BETTER LATER
       
        for kineticSet in np.arange(kinSet):
            for imageSet in np.arange(iterations):
                print kineticSet + 1, imageSet + 1
                parametersArray = self._fitInitialImage(data[kineticSet][numberImagesInSet*imageSet], kinSet, rows, cols, typicalIonDiameter, expectedNumberOfIons, initialParameters)
                self.kinSetParametersArray[iterations*kineticSet + imageSet] = tuple(parametersArray)
                for image in np.arange(numberImagesInSet):
                    axialSums = self._getOneDDdata(data[kineticSet][numberImagesInSet*imageSet + image], rows, cols, typicalIonDiameter) 
                        
                    
                    bestFitIonArrangement = [] # 1 = bright, 0 = dark, Ex: (1, 1, 0, 1, 1)
                    bestChiSquare = float(10000000) # get rid of this in the future and make the if statement a try/except
#                    bestDarkModel = []
                    positionValues = self.positionDict[str(expectedNumberOfIons)]
                    for ionArrangement in product(range(2), repeat=expectedNumberOfIons):
                        # build the model function, expected to have at least one component = 0 (have an ion dark in the model function)
                        darkModel = 0
                        for ion in np.arange(expectedNumberOfIons):
                            if ionArrangement[ion] == 1:
#                                print ionArrangement, ion
#                                print positionValues[ion]
                                darkModel += parametersArray[0]*np.exp(-(((xmodel-positionValues[ion]*parametersArray[1] - parametersArray[2])/parametersArray[3])**2)/2)
                        
                        darkModel += parametersArray[4]

                        
                        try:
                            tempChiSquare, pValue = chisquare(axialSums, darkModel)
                            if (tempChiSquare < bestChiSquare):
                                bestChiSquare = tempChiSquare
#                                bestDarkModel = darkModel
                                bestFitIonArrangement = ionArrangement
                        except AttributeError:
                            print 'loca!'
                        
                    self.bestModelFits[kineticSet].append(bestFitIonArrangement)
                    self.analysisTimes[kineticSet].append(str(datetime.time(datetime.now())))

#                    print 'best: ', bestChiSquare, bestFitIonArrangement
                    darkIonPositions = np.where(np.array(bestFitIonArrangement) == 0)[0] # awesome
#                    print darkIonPositions
                    if (image == 0):
                        darkIonPositionCatalog[kineticSet][imageSet].append(expectedNumberOfIons - len(darkIonPositions))
                    else:
                        darkIonPositionCatalog[kineticSet][imageSet].append(darkIonPositions)
#                    if ((imageSet == 0 and image == 0) or (imageSet == 1 and image == 0) or (imageSet == 1 and image == 0) or (imageSet == 11 and image == 0) or (imageSet == 14 and image == 1)):
#                        pyplot.plot(np.arange(len(axialSums)), axialSums)
#                        pyplot.plot(xmodel, bestDarkModel)
#                        print darkIonPositionCatalog
#                        show() 
        
        t2 = time.clock()
        print 'time: ', (t2-t1)      
        return darkIonPositionCatalog        


    def _fitInitialImage(self, data, kinSet, rows, cols, typicalIonDiameter, expectedNumberOfIons, initialParameters):
        """
        Since this method is called every iteration, the image data is passed into it.
        
        data = first image in an iteration.
        
        initialParameters = [alpha, axialOffset, sigma]
        
                            the offset and height are already approximated by the data"""        
        
        axialSums = self._getOneDDdata(data, rows, cols, typicalIonDiameter)
        
        
        # start here
    
        alpha = initialParameters[0] #Parameter(15)
        axialOffset = initialParameters[1] #Parameter(33)
        offset = np.min(axialSums)
        height = np.max(axialSums) - np.min(axialSums)
        sigma = initialParameters[2]            
    
        alpha, axialOffset, offset, height, sigma = self._fit(self._fitFunction, [height, alpha, axialOffset, sigma, offset], expectedNumberOfIons, axialSums)
#        print 'alpha: ', alpha
#        print 'axialOffset: ', axialOffset
#        print 'offset: ', offset
#        print 'height: ', height
#        print 'sigma: ', sigma
        
        return [alpha, axialOffset, offset, height, sigma]

    def _fit(self, function, parameters, expectedNumberOfIons, y, x = None):  
        solutions = [None]*len(parameters)
        def f(params):
            i = 0
            for p in params:
                solutions[i] = p
                i += 1
            return (y - function(x, params, expectedNumberOfIons))
        if x is None: x = np.arange(y.shape[0])
        optimize.leastsq(f, parameters)
        return solutions
    
    def _fitFunction(self, x, p, expectedNumberOfIons):
        """p = [height, alpha, axialOffset, sigma, offset] """   
        fitFunc = 0
        for i in self.positionDict[str(expectedNumberOfIons)]:
            fitFunc += p[0]*np.exp(-(((x-i*p[1] - p[2])/p[3])**2)/2)
    #    fitFunc = offset() + height()*exp(-(((x+1.7429*alpha())/sigma())**2)/2) + height()*exp(-(((x+0.8221*alpha())/sigma())**2)/2) + height()*exp(-(((x)/sigma())**2)/2) + height()*exp(-(((x-0.8221*alpha())/sigma())**2)/2) + height()*exp(-(((x-1.7429*alpha())/sigma())**2)/2)
        return fitFunc + p[4]

    def _getOneDDdata(self, data, rows, cols, typicalIonDiameter):
        """ The image, assumed to be have more columns than rows, will first be analyzed
            in the axial direction. The sums of the intensities will be collected in the
            axial direction first. This will help narrow down which section of the image,
            in order to exclude noise.
            
            Example:   |  [[ # # # # # # # # # # # # # # # # # # # # # #],       |
                       0   [ # # # # # # # # # # # # # # # # # # # # # #], avgIonDiameter
                       |   [ # # # # # # # # # # # # # # # # # # # # # #],       |
                      |    [ * * * * * * * * * * * * * * * * * * * * * *], <-- strip of highest intensity,
                      1    [ * * * * * * * * * * * * * * * * * * * * * *], <-- will only be used for 
                      |    [ * * * * * * * * * * * * * * * * * * * * * *], <-- proceeding calculations
                       |   [ % % % % % % % % % % % % % % % % % % % % % %],
                       2   [ % % % % % % % % % % % % % % % % % % % % % %],
                       |   [ % % % % % % % % % % % % % % % % % % % % % %]]
                                  
                                             Axial   
        """
        
        
        axialSumSegments = []
        axialData = np.sum(data, 1) # 1D vector: sum of intensities in the axial direction. length = rows

        
        """ choose each strip by only analyzing the 1D vector of sums
            
            [ # # # * * * % % %] -> [# * %]
                                     0 1 2
                      ^                ^
                      |                |
                    Segment           most
                                    intense
                                      sum
        """
        intensitySum = 0
        cnt = 0
        for i in np.arange(rows):
            intensitySum += axialData[i]
            cnt += 1
            if (cnt == typicalIonDiameter):
                axialSumSegments.append(intensitySum)
                cnt = 0
                intensitySum = 0 
                
        # find the index of the strip with the highest intensity
        mostIntenseRegionIndex = np.where(axialSumSegments == np.max(axialSumSegments))[0][0]
        
        """ use this strip to create the 1-dimensional array of intensity sums in the radial direction
        
            [ * * * * * * * * * * * * * * * * * * * * * *] 1D vector of sums
                                                            in the radial direction
                                  ^                            length = cols
                                  |                        Used to find peaks
           
           [[ * * * * * * * * * * * * * * * * * * * * * *], most 
            [ * * * * * * * * * * * * * * * * * * * * * *], intense
            [ * * * * * * * * * * * * * * * * * * * * * *]]  strip
            
            
        
        """


        mostIntenseData = data[(mostIntenseRegionIndex*typicalIonDiameter):(mostIntenseRegionIndex*typicalIonDiameter + typicalIonDiameter), :]
        mostIntenseDataSums = np.sum(mostIntenseData, 0)# / typicalIonDiameter #1D vector
#        mostIntenseDataSums = (mostIntenseDataSums - np.min(mostIntenseDataSums))/(np.max(mostIntenseDataSums) - np.min(mostIntenseDataSums))
        mostIntenseDataSums = mostIntenseDataSums / np.sum(mostIntenseDataSums) # normalized to 1 (divided by the area under the curve)
                
        return mostIntenseDataSums

    @inlineCallbacks
    def _appendParametersToDatasets(self, kinSet, numKin, iterations):
        
        
        numberImagesInSet = (numKin / iterations)
        
        dv = self.server
        for kineticSet in np.arange(kinSet):
            yield dv.cd(self.directoryList[kineticSet])
            for imageSet in np.arange(iterations):
                for image in np.arange(numberImagesInSet):
                    yield dv.open(int(numberImagesInSet*imageSet + image + 1))
                    # check if the parameters exist first!!! don't append more for the hell of it
                    try:
                        yield dv.add_parameter_over_write(['Parameters', self.kinSetParametersArray[iterations*kineticSet + imageSet]])
                        yield dv.add_parameter_over_write(['Arrangement', self.bestModelFits[kineticSet][numberImagesInSet*imageSet + image]])
                        yield dv.add_parameter_over_write(['Time', self.analysisTimes[kineticSet][numberImagesInSet*imageSet + image]])
                    except:
                        print 'passed!' 

    def _getIonNumberCatalog(self, image, darkIonPositionCatalog, iterations, kinSet, numKin):
        """image = 1, 2, or 3 
        
           Note: the array is in order of kinetic set and iteration
        """
        
        numberKineticSets = kinSet
        
        ionNumberCatalog = []
        
        for kinSet in np.arange(numberKineticSets):
            for iteration in np.arange(iterations):
                if (image == 1):
                    ionNumberCatalog.append(darkIonPositionCatalog[kinSet][iteration][image - 1]) # since the first value is already the ion number
                else:    
                    ionNumberCatalog.append(len(darkIonPositionCatalog[kinSet][iteration][image - 1]))
        
        return ionNumberCatalog

    def _buildIonSwapCatalog(self, darkIonPositionCatalog, kinSet, iterations, expectedNumberOfIons):
        """  returns a 1D array describing the distance an ion travelled by comparing the initial
             and final images.
         
             this assumes 2 images to be analyzed per background image. Also assumes that there is 
             only ONE dark ion in both images.
             
             Note: the array is in order of kinetic set
             
         """
        
       
        numberKineticSets = kinSet
        ionSwapCatalog = []
        
        for kinSet in np.arange(numberKineticSets):
            for imageSet in np.arange(iterations):
                if (darkIonPositionCatalog[kinSet][imageSet][0] == expectedNumberOfIons):
                    if (len(darkIonPositionCatalog[kinSet][imageSet][1]) == 1):
                        initialPosition = darkIonPositionCatalog[kinSet][imageSet][1]
                        if (len(darkIonPositionCatalog[kinSet][imageSet][2]) == 1):
                            finalPosition = darkIonPositionCatalog[kinSet][imageSet][2]                  
                            ionSwapCatalog.append(abs(finalPosition - initialPosition))
                
#                print 'number ions in first image: ', darkIonPositionCatalog[kinSet][imageSet][0]
#                print 'number dark ions in second image: ', len(darkIonPositionCatalog[kinSet][imageSet][1])
#                print 'number dark ions in third image: ', len(darkIonPositionCatalog[kinSet][imageSet][2])

#        print 'ion swap catalog:'
#        print ionSwapCatalog
        print 'len of ion swap catalog: ', len(ionSwapCatalog)
        return ionSwapCatalog


if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    ionCount = IonCount(reactor)
    reactor.run()
    
