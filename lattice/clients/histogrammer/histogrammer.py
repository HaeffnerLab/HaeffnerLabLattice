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

class HistCanvas(FigureCanvas):
    """Matplotlib Figure widget to display CPU utilization"""
    def __init__(self, parent, ionCatalogArray, ionSwapCatalog):
        self.parent = parent
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)

        self.ax = self.fig.add_subplot(111)
      
        ax.hist(data, bins=range(10), align='left', normed=True, label = label)
        ax.legend(loc='best')
        #self.ax.set_ylim(0, 1)
               
        
class HistWindow(QtGui.QWidget):        
    """Creates the window for the new plot"""
    def __init__(self, parent, data):
        QtGui.QWidget.__init__(self)
        
        self.parent = parent
        
        layout = QtGui.QVBoxLayout()
        
        #try:
        canvas = HistCanvas(self, data)
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

class Histogrammer(QtGui.QWidget):        
    """Creates the window for the new plot"""
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        
        self.parent = parent
        self.histList = []

        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        try:
            self.server = yield self.cxn.data_vault
        except Exception ,e:
            print 'server not connected: {}'.format(e)        

        self.setupDataVaultWidget()       


    @inlineCallbacks
    def setupDataVaultWidget(self):    
        context = yield self.cxn.context()
        self.datavaultwidget = DataVaultWidget(self, context)
        self.datavaultwidget.populateList()
#        self.datavaultwidget.show()     
        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(self.datavaultwidget)
        
        self.setLayout(self.layout)
        
    @inlineCallbacks
    def newHistogram(self, dataset, directory):
        yield self.server.cd(directory)
        yield self.server.open(dataset)
        Data = yield self.server.get()
        data = Data.asarray
        
        histWindow = HistWindow(self, data)
        self.histList.append(histWindow)
        histWindow.show()        

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    histogrammer = Histogrammer(reactor)
    histogrammer.show()
    reactor.run()
