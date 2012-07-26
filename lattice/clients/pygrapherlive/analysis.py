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
        self.analysisCheckboxes = {}      
        self.fitCurveDictionary = {'Line': self.fitLine,
                                   'Gaussian': self.fitGaussian
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
        fitButton = QtGui.QPushButton("Fit Curves", self)
        fitButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        fitButton.clicked.connect(self.fitCurves)        
        mainLayout.addWidget(fitButton)
        
        self.setLayout(mainLayout)        


    def fitCurves(self, evt):
        for dataset,directory,index in self.parent.datasetAnalysisCheckboxes.keys():
            # if dataset is intended to be drawn (a checkbox governs this)
            if self.parent.datasetAnalysisCheckboxes[dataset, directory, index].isChecked():
                for key in self.analysisCheckboxes.keys():
                    if self.analysisCheckboxes[key].isChecked():
                        labels = self.parent.qmc.datasetLabelsDict[dataset, directory]
                        print dataset, directory, index, key
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
        directory[-1] += ' Line Model'
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
        directory[-1] += ' Gaussian Model'
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
    