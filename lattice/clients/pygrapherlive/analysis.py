'''
Analysis Widget
'''
from PyQt4 import QtCore, QtGui
import numpy as np
from scipy import optimize

class AnalysisWidget(QtGui.QWidget):
    """Creates the window for the new plot"""
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)  
        self.parent = parent     
        self.parameterWindow = ParameterWindow(self)
        self.analysisCheckboxes = {}      
        self.fitCurveDictionary = {'Line': self.fitLine,
                                   'Gaussian': self.fitGaussian,
                                   'Lorentzian': self.fitLorentzian
                                   }   
        self.setMaximumWidth(180)

        mainLayout = QtGui.QVBoxLayout()
                
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(5)
        
        title = QtGui.QLabel()
        title.setText('Analysis')
              
        dummyLayout = QtGui.QHBoxLayout()
        mainLayout.addLayout(dummyLayout)
        dummyLayout.addWidget(title, QtCore.Qt.AlignCenter)

        self.analysisCheckboxes['Gaussian'] = QtGui.QCheckBox('Gaussian', self)
        self.analysisCheckboxes['Lorentzian'] = QtGui.QCheckBox('Lorentzian', self)
        self.analysisCheckboxes['Parabola'] = QtGui.QCheckBox('Parabola', self)
        self.analysisCheckboxes['Line'] = QtGui.QCheckBox('Line', self)
               
        self.grid.addWidget(self.analysisCheckboxes['Gaussian'], 1, 0, QtCore.Qt.AlignLeft)
        self.grid.addWidget(self.analysisCheckboxes['Lorentzian'], 1, 1, QtCore.Qt.AlignLeft)
        self.grid.addWidget(self.analysisCheckboxes['Parabola'], 2, 0, QtCore.Qt.AlignLeft)
        self.grid.addWidget(self.analysisCheckboxes['Line'], 2, 1, QtCore.Qt.AlignLeft)       
        
        mainLayout.addLayout(self.grid)
        
        # Layout for keeping track of datasets on a graph and analysis
        self.datasetCheckboxListWidget = QtGui.QListWidget()
        self.datasetCheckboxListWidget.setMaximumWidth(180)
        self.datasetCheckboxListWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        mainLayout.addWidget(self.datasetCheckboxListWidget)

        # button to fit data on screen
        parametersButton = QtGui.QPushButton("Parameters", self)
        parametersButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        parametersButton.clicked.connect(self.setParameters)        
        mainLayout.addWidget(parametersButton)
        
        # button to fit data on screen
        fitButton = QtGui.QPushButton("Fit Curves", self)
        fitButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        fitButton.clicked.connect(self.fitCurves)        
        mainLayout.addWidget(fitButton)
        
        self.setLayout(mainLayout)        


    def setParameters(self, evt):
        self.parameterWindow.show()
        # create the parameter window upstairs, spinboxes will be part of it

    def fitCurves(self, evt):
        for dataset,directory,index in self.parent.datasetAnalysisCheckboxes.keys():
            # if dataset is intended to be drawn (a checkbox governs this)
            if self.parent.datasetAnalysisCheckboxes[dataset, directory, index].isChecked():
                for key in self.analysisCheckboxes.keys():
                    if self.analysisCheckboxes[key].isChecked():
                        labels = self.parent.qmc.datasetLabelsDict[dataset, directory]
#                        print dataset, directory, index, key
                        # MULTIPLE LINES IN THE SAME DATASET!!!!
                        fitFunction = self.fitCurveDictionary[key]
                        fitFunction(dataset, directory, index, labels[index])
                        
    def fitLine(self, dataset, directory, index, label):
        dataX, dataY = self.parent.qmc.plotDict[dataset, directory][index].get_data() # dependent variable
        slope = (np.max(dataY) - np.min(dataY))/(np.max(dataX) - np.min(dataX))
        offset = np.min(dataY)
        slope, offset = self.fit(self.fitFuncLine, [slope, offset], dataY, dataX)
        
        modelX = np.linspace(dataX[0], dataX[-1], len(dataX)*2)
        modelY = self.fitFuncLine(modelX, [slope, offset])
        plotData = np.vstack((modelX, modelY)).transpose()
        
        directory = list(directory)
        directory[-1] += ' - '
        directory[-1] += label
        directory[-1] += ' - '
        directory[-1] += 'Line Model'
        directory = tuple(directory)
        
        self.parent.qmc.initializeDataset(dataset, directory, (label + ' Line Model',))
        self.parent.qmc.setPlotData(dataset, directory, plotData)
    
    def fitFuncLine(self, x, p):
        """ 
            Line
            p = [slope, offset]
        """   
        fitFunc = p[0]*x + p[1]
#        fitFunc += p[0]*np.exp(-(((x-i*p[1] - p[2])/p[3])**2)/2) # gaussian
        return fitFunc

    def fitGaussian(self, dataset, directory, index, label):
        dataX, dataY = self.parent.qmc.plotDict[dataset, directory][index].get_data() # dependent variable
        
        xValues = np.arange(len(dataY))
        center = np.sum(xValues*dataY)/np.sum(dataY)
        sigma = np.abs(np.sum((xValues - center)**2*dataY/np.sum(dataY)))
        height = np.max(dataY)
        offset = np.min(dataY)
               
        height, center, sigma, offset = self.fit(self.fitFuncGaussian, [height, center, sigma, offset], dataY, dataX)
               
        modelX = np.linspace(dataX[0], dataX[-1], len(dataX)*2)
        modelY = self.fitFuncGaussian(modelX, [height, center, sigma, offset])
        plotData = np.vstack((modelX, modelY)).transpose()
        
        directory = list(directory)
        directory[-1] += ' - '
        directory[-1] += label
        directory[-1] += ' - '
        directory[-1] += 'Gaussian Model'
        directory = tuple(directory)
        
        self.parent.qmc.initializeDataset(dataset, directory, (label + ' Gaussian Model',))
        self.parent.qmc.setPlotData(dataset, directory, plotData)
    
    def fitFuncGaussian(self, x, p):
        """ 
            Gaussian
            p = [height, center, sigma, offset]
        
        """   
        fitFunc = p[0]*np.exp(-(((x - p[1])/p[2])**2)/2) + p[3]# gaussian
        return fitFunc

    def fitLorentzian(self, dataset, directory, index, label):
        dataX, dataY = self.parent.qmc.plotDict[dataset, directory][index].get_data() # dependent variable
        
        xValues = np.arange(len(dataY))
        print len(dataY)
        center = dataX[np.sum(xValues*dataY)/np.sum(dataY)]
        offset = np.min(dataY)
        gamma = 10
        I = np.max(dataY) - np.min(dataY)
        
        print gamma, center, I, offset
        
        
        gamma, center, I, offset = self.fit(self.fitFuncLorentzian, [gamma, center, I, offset], dataY, dataX)

        print gamma, center, I, offset
               
        modelX = np.linspace(dataX[0], dataX[-1], len(dataX)*2)
        modelY = self.fitFuncLorentzian(modelX, [gamma, center, I, offset])
        plotData = np.vstack((modelX, modelY)).transpose()
        
        directory = list(directory)
        directory[-1] += ' - '
        directory[-1] += label
        directory[-1] += ' - '
        directory[-1] += 'Lorentzian Model'
        directory = tuple(directory)
        
        self.parent.qmc.initializeDataset(dataset, directory, (label + ' Lorentzian Model',))
        self.parent.qmc.setPlotData(dataset, directory, plotData)
    
    def fitFuncLorentzian(self, x, p):
        """ 
            Lorentzian
            p = [gamma, center, I, offset]
        
        """   
        fitFunc = p[3] + p[2]*(p[0]**2/((x - p[1])**2 + p[0]**2))# Lorentzian
        return fitFunc

    
    def fit(self, function, parameters, y, x = None):  
        solutions = [None]*len(parameters)
        def f(params):
            i = 0
            for p in params:
                solutions[i] = p
                i += 1
            return (y - function(x, params))
        if x is None: x = np.arange(y.shape[0])
        optimize.leastsq(f, parameters)
        return solutions

class ParameterWindow(QtGui.QWidget):
    """Creates the device parameter window"""

    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.setWindowTitle('Analysis Parameters')
        self.setupUI()
    
    def setupUI(self):
        # Title Labels
        gaussianLabel = QtGui.QLabel('Gaussian:  Height*exp(-(((x - center)/Sigma)**2)/2) + Offset')
        lorentzianLabel = QtGui.QLabel('Lorentzian: Offset + I*(Gamma**2/((x - Center)**2 + Gamma**2))')
        lineLabel = QtGui.QLabel('Line: Slope*x + Offset')
        parabolaLabel = QtGui.QLabel('Parabola: A*x**2 + B*x + C ')

        # Gaussian

        gaussianHeightLabel = QtGui.QLabel('Height')
        self.gaussianHeightDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.gaussianHeightDoubleSpinBox.setDecimals(4)
        self.gaussianHeightDoubleSpinBox.setMinimum(0)
        self.gaussianHeightDoubleSpinBox.setSingleStep(.01)
        self.gaussianHeightDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        gaussianCenterLabel = QtGui.QLabel('Center')
        self.gaussianCenterDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.gaussianCenterDoubleSpinBox.setDecimals(4)
        self.gaussianCenterDoubleSpinBox.setMinimum(0)
        self.gaussianCenterDoubleSpinBox.setSingleStep(.01)
        self.gaussianCenterDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
         
        gaussianSigmaLabel = QtGui.QLabel('Sigma')
        self.gaussianSigmaDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.gaussianSigmaDoubleSpinBox.setDecimals(4)
        self.gaussianSigmaDoubleSpinBox.setMinimum(0)
        self.gaussianSigmaDoubleSpinBox.setSingleStep(.01)
        self.gaussianSigmaDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        gaussianOffsetLabel = QtGui.QLabel('Offset')
        self.gaussianOffsetDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.gaussianOffsetDoubleSpinBox.setDecimals(4)
        self.gaussianOffsetDoubleSpinBox.setMinimum(0)
        self.gaussianOffsetDoubleSpinBox.setSingleStep(.01)
        self.gaussianOffsetDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        # Lorentzian

        lorentzianGammaLabel = QtGui.QLabel('Gamma')
        self.lorentzianGammaDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.lorentzianGammaDoubleSpinBox.setDecimals(4)
        self.lorentzianGammaDoubleSpinBox.setMinimum(0)
        self.lorentzianGammaDoubleSpinBox.setSingleStep(.01)
        self.lorentzianGammaDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        lorentzianCenterLabel = QtGui.QLabel('Center')
        self.lorentzianCenterDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.lorentzianCenterDoubleSpinBox.setDecimals(4)
        self.lorentzianCenterDoubleSpinBox.setMinimum(0)
        self.lorentzianCenterDoubleSpinBox.setSingleStep(.01)
        self.lorentzianCenterDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
         
        lorentzianILabel = QtGui.QLabel('I')
        self.lorentzianIDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.lorentzianIDoubleSpinBox.setDecimals(4)
        self.lorentzianIDoubleSpinBox.setMinimum(0)
        self.lorentzianIDoubleSpinBox.setSingleStep(.01)
        self.lorentzianIDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        lorentzianOffsetLabel = QtGui.QLabel('Offset')
        self.lorentzianOffsetDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.lorentzianOffsetDoubleSpinBox.setDecimals(4)
        self.lorentzianOffsetDoubleSpinBox.setMinimum(0)
        self.lorentzianOffsetDoubleSpinBox.setSingleStep(.01)
        self.lorentzianOffsetDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        # Line

        lineSlopeLabel = QtGui.QLabel('Slope')
        self.lineSlopeDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.lineSlopeDoubleSpinBox.setDecimals(4)
        self.lineSlopeDoubleSpinBox.setMinimum(0)
        self.lineSlopeDoubleSpinBox.setSingleStep(.01)
        self.lineSlopeDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        lineOffsetLabel = QtGui.QLabel('Offset')
        self.lineOffsetDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.lineOffsetDoubleSpinBox.setDecimals(4)
        self.lineOffsetDoubleSpinBox.setMinimum(0)
        self.lineOffsetDoubleSpinBox.setSingleStep(.01)
        self.lineOffsetDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        # Parabola

        parabolaALabel = QtGui.QLabel('A')
        self.parabolaADoubleSpinBox = QtGui.QDoubleSpinBox()
        self.parabolaADoubleSpinBox.setDecimals(4)
        self.parabolaADoubleSpinBox.setMinimum(0)
        self.parabolaADoubleSpinBox.setSingleStep(.01)
        self.parabolaADoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        parabolaBLabel = QtGui.QLabel('B')
        self.parabolaBDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.parabolaBDoubleSpinBox.setDecimals(4)
        self.parabolaBDoubleSpinBox.setMinimum(0)
        self.parabolaBDoubleSpinBox.setSingleStep(.01)
        self.parabolaBDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        parabolaCLabel = QtGui.QLabel('C')
        self.parabolaCDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.parabolaCDoubleSpinBox.setDecimals(4)
        self.parabolaCDoubleSpinBox.setMinimum(0)
        self.parabolaCDoubleSpinBox.setSingleStep(.01)
        self.parabolaCDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        # Layout
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)
        self.grid.setSpacing(5)
        
        # Gaussian
        self.grid.addWidget(gaussianLabel, 1, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(gaussianHeightLabel, 1, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.gaussianHeightDoubleSpinBox, 1, 2, QtCore.Qt.AlignCenter)
        self.grid.addWidget(gaussianCenterLabel, 1, 3, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.gaussianCenterDoubleSpinBox, 1, 4, QtCore.Qt.AlignCenter)
        self.grid.addWidget(gaussianSigmaLabel, 1, 5, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.gaussianSigmaDoubleSpinBox, 1, 6, QtCore.Qt.AlignCenter)
        self.grid.addWidget(gaussianOffsetLabel, 1, 7, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.gaussianOffsetDoubleSpinBox, 1, 8, QtCore.Qt.AlignCenter)
 
        # Lorentzian
        self.grid.addWidget(lorentzianLabel, 3, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(lorentzianGammaLabel, 3, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.lorentzianGammaDoubleSpinBox, 3, 2, QtCore.Qt.AlignCenter)
        self.grid.addWidget(lorentzianCenterLabel, 3, 3, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.lorentzianCenterDoubleSpinBox, 3, 4, QtCore.Qt.AlignCenter)
        self.grid.addWidget(lorentzianILabel, 3, 5, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.lorentzianIDoubleSpinBox, 3, 6, QtCore.Qt.AlignCenter)
        self.grid.addWidget(lorentzianOffsetLabel, 3, 7, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.lorentzianOffsetDoubleSpinBox, 3, 8, QtCore.Qt.AlignCenter)

        # Line
        self.grid.addWidget(lineLabel, 5, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(lineSlopeLabel, 5, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.lineSlopeDoubleSpinBox, 5, 2, QtCore.Qt.AlignCenter)
        self.grid.addWidget(lineOffsetLabel, 5, 3, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.lineOffsetDoubleSpinBox, 5, 4, QtCore.Qt.AlignCenter)
 
        # Parabola
        self.grid.addWidget(parabolaLabel, 7, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(parabolaALabel, 7, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.parabolaADoubleSpinBox, 7, 2, QtCore.Qt.AlignCenter)
        self.grid.addWidget(parabolaBLabel, 7, 3, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.parabolaBDoubleSpinBox, 7, 4, QtCore.Qt.AlignCenter)
        self.grid.addWidget(parabolaCLabel, 7, 5, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.parabolaCDoubleSpinBox, 7, 6, QtCore.Qt.AlignCenter)
        
        self.setFixedSize(800, 200)


    def closeEvent(self, evt):
        self.hide()        
   