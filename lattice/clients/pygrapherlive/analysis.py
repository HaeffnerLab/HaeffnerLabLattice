'''
Analysis Widget
'''
from PyQt4 import QtCore, QtGui

class AnalysisWidget(QtGui.QWidget):
    """Creates the window for the new plot"""
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)  
        self.parent = parent     
        self.analysisCheckboxes = {}      
        self.fitCurveDictionary = {'Line': self.fitLine}   
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
        mainLayout.addWidget(self.datasetCheckboxListWidget)
        
        # button to fit data on screen
        fitButton = QtGui.QPushButton("Fit Curves", self)
        fitButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        fitButton.clicked.connect(self.fitCurves)        
        mainLayout.addWidget(fitButton)
        
        self.setLayout(mainLayout)        


    def fitCurves(self, evt):
        for dataset,directory, index in self.parent.datasetAnalysisCheckboxes.keys():
            # if dataset is intended to be drawn (a checkbox governs this)
            if self.parent.datasetAnalysisCheckboxes[dataset, directory, index].isChecked():
                for key in self.analysisCheckboxes.keys():
                    if self.analysisCheckboxes[key].isChecked():
                        print dataset, directory, index, key
                        # MULTIPLE LINES IN THE SAME DATASET!!!!
                        fitFunction = self.fitCurveDictionary[key]
                        fitFunction()
                        
    def fitLine(self):
        parameters = [1, 5]
        print parameters
    
    def fitFuncLine(self, x, p, expectedNumberOfIons):
        """p = [slope, offset] """   
        fitFunc = 0
        for i in self.positionDict[str(expectedNumberOfIons)]:
            fitFunc += p[0]*np.exp(-(((x-i*p[1] - p[2])/p[3])**2)/2)
    #    fitFunc = offset() + height()*exp(-(((x+1.7429*alpha())/sigma())**2)/2) + height()*exp(-(((x+0.8221*alpha())/sigma())**2)/2) + height()*exp(-(((x)/sigma())**2)/2) + height()*exp(-(((x-0.8221*alpha())/sigma())**2)/2) + height()*exp(-(((x-1.7429*alpha())/sigma())**2)/2)
        return fitFunc + p[4]
    
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
    