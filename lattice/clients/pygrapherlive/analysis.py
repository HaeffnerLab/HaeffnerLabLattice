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
                                   'Lorentzian': self.fitLorentzian,
                                   'Parabola': self.fitParabola
                                   }   
        self.solutionsDictionary = {}
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
        fitButton.clicked.connect(self.fitCurvesSignal)        
        mainLayout.addWidget(fitButton)
        
        self.setLayout(mainLayout)        


    def setParameters(self, evt):
        self.parameterWindow.show()
        # create the parameter window upstairs, spinboxes will be part of it

    def fitCurvesSignal(self, evt):
        self.fitCurves()

    def fitCurves(self, parameters = None):
        self.solutionsDictionary = {}
        for dataset,directory,index in self.parent.datasetAnalysisCheckboxes.keys():
            # if dataset is intended to be drawn (a checkbox governs this)
            if self.parent.datasetAnalysisCheckboxes[dataset, directory, index].isChecked():
                for key in self.analysisCheckboxes.keys():
                    if self.analysisCheckboxes[key].isChecked():
                        labels = self.parent.qmc.datasetLabelsDict[dataset, directory]
#                        print dataset, directory, index, key
                        # MULTIPLE LINES IN THE SAME DATASET!!!!
                        fitFunction = self.fitCurveDictionary[key]
                        fitFunction(dataset, directory, index, labels[index], parameters)
        self.solutionsWindow = SolutionsWindow(self.solutionsDictionary)
        self.solutionsWindow.show()

    def fitGaussian(self, dataset, directory, index, label, parameters):
        dataX, dataY = self.parent.qmc.plotDict[dataset, directory][index].get_data() # dependent variable
        
#        xValues = np.arange(len(dataY))
#        center = np.sum(xValues*dataY)/np.sum(dataY)
#        sigma = np.abs(np.sum((xValues - center)**2*dataY/np.sum(dataY)))
#        height = np.max(dataY)
#        offset = np.min(dataY)
        
        if (parameters == None): 
            height = self.parameterWindow.gaussianHeightDoubleSpinBox.value()
            center = self.parameterWindow.gaussianCenterDoubleSpinBox.value()
            sigma =  self.parameterWindow.gaussianSigmaDoubleSpinBox.value()
            offset = self.parameterWindow.gaussianOffsetDoubleSpinBox.value()
        else:
            height = parameters[0]
            center = parameters[1]
            sigma =  parameters[2]
            offset = parameters[3]
            
               
        height, center, sigma, offset = self.fit(self.fitFuncGaussian, [height, center, sigma, offset], dataY, dataX)
        
        self.solutionsDictionary[dataset, directory, label, 'Gaussian', '[Height, Center, Sigma, Offset]'] = [height, center, sigma, offset]
               
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

    def fitLorentzian(self, dataset, directory, index, label, parameters):
        dataX, dataY = self.parent.qmc.plotDict[dataset, directory][index].get_data() # dependent variable
        
#        xValues = np.arange(len(dataY))
#        print len(dataY)
#        center = dataX[np.sum(xValues*dataY)/np.sum(dataY)]
#        offset = np.min(dataY)
#        gamma = 10
#        I = np.max(dataY) - np.min(dataY)
        
        if (parameters == None):
            gamma = self.parameterWindow.lorentzianGammaDoubleSpinBox.value()
            center = self.parameterWindow.lorentzianCenterDoubleSpinBox.value()
            I = self.parameterWindow.lorentzianIDoubleSpinBox.value()
            offset = self.parameterWindow.lorentzianOffsetDoubleSpinBox.value()
        else:
            gamma = parameters[0]
            center = parameters[1]
            I = parameters[2]
            offset = parameters[3]
           
        
        gamma, center, I, offset = self.fit(self.fitFuncLorentzian, [gamma, center, I, offset], dataY, dataX)
        
        self.solutionsDictionary[dataset, directory, label, 'Lorentzian', '[Gamma, Center, I, Offset]'] = [gamma, center, I, offset] 
               
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

    def fitLine(self, dataset, directory, index, label, parameters):
        dataX, dataY = self.parent.qmc.plotDict[dataset, directory][index].get_data() # dependent variable
#        slope = (np.max(dataY) - np.min(dataY))/(np.max(dataX) - np.min(dataX))
#        offset = np.min(dataY)
        
        if (parameters == None):
            slope = self.parameterWindow.lineSlopeDoubleSpinBox.value()
            offset = self.parameterWindow.lineOffsetDoubleSpinBox.value()
        else:
            slope = parameters[0]
            offset = parameters[1]
            
        slope, offset = self.fit(self.fitFuncLine, [slope, offset], dataY, dataX)
        
        self.solutionsDictionary[dataset, directory, label, 'Line', '[Slope, Offset]'] = [slope, offset] 
        
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
        return fitFunc
    
    def fitParabola(self, dataset, directory, index, label, parameters):
        dataX, dataY = self.parent.qmc.plotDict[dataset, directory][index].get_data() # dependent variable
#        A = 5
#        B = (np.max(dataY) - np.min(dataY))/(np.max(dataX) - np.min(dataX))
#        C = np.min(dataY)

        if (parameters == None):
            A = self.parameterWindow.parabolaADoubleSpinBox.value()
            B = self.parameterWindow.parabolaBDoubleSpinBox.value()
            C = self.parameterWindow.parabolaCDoubleSpinBox.value()
        else:
            A = parameters[0]
            B = parameters[1]
            C = parameters[2]

        A, B, C = self.fit(self.fitFuncParabola, [A, B, C], dataY, dataX)
        
        self.solutionsDictionary[dataset, directory, label, 'Parabola', '[A, B, C]'] = [A, B, C] 
        
        modelX = np.linspace(dataX[0], dataX[-1], len(dataX)*2)
        modelY = self.fitFuncParabola(modelX, [A, B, C])
        plotData = np.vstack((modelX, modelY)).transpose()
        
        directory = list(directory)
        directory[-1] += ' - '
        directory[-1] += label
        directory[-1] += ' - '
        directory[-1] += 'Parabola Model'
        directory = tuple(directory)
        
        self.parent.qmc.initializeDataset(dataset, directory, (label + ' Parabola Model',))
        self.parent.qmc.setPlotData(dataset, directory, plotData)
    
    def fitFuncParabola(self, x, p):
        """ 
            Parabola
            A*x**2 + B*x + C
            p = [A, B, C]
        """   
        fitFunc = p[0]*x**2 + p[1]*x + p[2]
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
    """Creates the fitting parameter window"""

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
        self.gaussianHeightDoubleSpinBox.setDecimals(6)
        self.gaussianHeightDoubleSpinBox.setRange(-1000000000, 1000000000)
        self.gaussianHeightDoubleSpinBox.setValue(1)
        self.gaussianHeightDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        gaussianCenterLabel = QtGui.QLabel('Center')
        self.gaussianCenterDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.gaussianCenterDoubleSpinBox.setDecimals(6)
        self.gaussianCenterDoubleSpinBox.setRange(-1000000000, 1000000000)
        self.gaussianCenterDoubleSpinBox.setValue(1)
        self.gaussianCenterDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
         
        gaussianSigmaLabel = QtGui.QLabel('Sigma')
        self.gaussianSigmaDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.gaussianSigmaDoubleSpinBox.setDecimals(6)
        self.gaussianSigmaDoubleSpinBox.setRange(-1000000000, 1000000000)
        self.gaussianSigmaDoubleSpinBox.setValue(1)
        self.gaussianSigmaDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        gaussianOffsetLabel = QtGui.QLabel('Offset')
        self.gaussianOffsetDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.gaussianOffsetDoubleSpinBox.setDecimals(6)
        self.gaussianOffsetDoubleSpinBox.setRange(-1000000000, 1000000000)
        self.gaussianOffsetDoubleSpinBox.setValue(1)
        self.gaussianOffsetDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        # Lorentzian

        lorentzianGammaLabel = QtGui.QLabel('Gamma')
        self.lorentzianGammaDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.lorentzianGammaDoubleSpinBox.setDecimals(6)
        self.lorentzianGammaDoubleSpinBox.setRange(-1000000000, 1000000000)
        self.lorentzianGammaDoubleSpinBox.setValue(1)
        self.lorentzianGammaDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        lorentzianCenterLabel = QtGui.QLabel('Center')
        self.lorentzianCenterDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.lorentzianCenterDoubleSpinBox.setDecimals(6)
        self.lorentzianCenterDoubleSpinBox.setRange(-1000000000, 1000000000)
        self.lorentzianCenterDoubleSpinBox.setValue(1)
        self.lorentzianCenterDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
         
        lorentzianILabel = QtGui.QLabel('I')
        self.lorentzianIDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.lorentzianIDoubleSpinBox.setDecimals(6)
        self.lorentzianIDoubleSpinBox.setRange(-1000000000, 1000000000)
        self.lorentzianIDoubleSpinBox.setValue(1)
        self.lorentzianIDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        lorentzianOffsetLabel = QtGui.QLabel('Offset')
        self.lorentzianOffsetDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.lorentzianOffsetDoubleSpinBox.setDecimals(6)
        self.lorentzianOffsetDoubleSpinBox.setRange(-1000000000, 1000000000)
        self.lorentzianOffsetDoubleSpinBox.setValue(1)
        self.lorentzianOffsetDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        # Line

        lineSlopeLabel = QtGui.QLabel('Slope')
        self.lineSlopeDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.lineSlopeDoubleSpinBox.setDecimals(6)
        self.lineSlopeDoubleSpinBox.setRange(-1000000000, 1000000000)
        self.lineSlopeDoubleSpinBox.setValue(1)
        self.lineSlopeDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        lineOffsetLabel = QtGui.QLabel('Offset')
        self.lineOffsetDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.lineOffsetDoubleSpinBox.setDecimals(6)
        self.lineOffsetDoubleSpinBox.setRange(-1000000000, 1000000000)
        self.lineOffsetDoubleSpinBox.setValue(1)
        self.lineOffsetDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        # Parabola

        parabolaALabel = QtGui.QLabel('A')
        self.parabolaADoubleSpinBox = QtGui.QDoubleSpinBox()
        self.parabolaADoubleSpinBox.setDecimals(6)
        self.parabolaADoubleSpinBox.setRange(-1000000000, 1000000000)
        self.parabolaADoubleSpinBox.setValue(1)
        self.parabolaADoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        parabolaBLabel = QtGui.QLabel('B')
        self.parabolaBDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.parabolaBDoubleSpinBox.setDecimals(6)
        self.parabolaBDoubleSpinBox.setRange(-1000000000, 1000000000)
        self.parabolaBDoubleSpinBox.setValue(1)
        self.parabolaBDoubleSpinBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        parabolaCLabel = QtGui.QLabel('C')
        self.parabolaCDoubleSpinBox = QtGui.QDoubleSpinBox()
        self.parabolaCDoubleSpinBox.setDecimals(6)
        self.parabolaCDoubleSpinBox.setRange(-1000000000, 1000000000)
        self.parabolaCDoubleSpinBox.setValue(1)
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
        
        self.setFixedSize(1000, 200)


    def closeEvent(self, evt):
        self.hide()        

class SolutionsWindow(QtGui.QWidget):
    """Creates the fitting parameter window"""

    def __init__(self, solutionsDictionary):
        QtGui.QWidget.__init__(self)
        self.solutionsDictionary = solutionsDictionary
        self.labels = []
        self.textBoxes = []
        self.setWindowTitle('Solutions')
        self.setupUI()
   
    def setupUI(self):
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(5)        
        
        for dataset, directory, label, curve, parameters in self.solutionsDictionary.keys():
            datasetLabel = QtGui.QLabel(str(dataset) + ' - ' + str(directory[-1]) + ' - ' + label)
            self.labels.append(datasetLabel)
            textBox = QtGui.QLineEdit(readOnly=True)
            textBox.setText('\'Fit\', [\'[]\', \''+ str(curve) + '\', ' + '\'' + str(self.solutionsDictionary[dataset, directory, label, curve, parameters]) + '\']')
            textBox.setMinimumWidth(550)
            self.textBoxes.append(textBox)
        
        for i in range(len(self.labels)):
            self.grid.addWidget(self.labels[i], i, 0, QtCore.Qt.AlignCenter)
            self.grid.addWidget(self.textBoxes[i], i, 1, QtCore.Qt.AlignCenter)

        self.setLayout(self.grid)
        self.show()