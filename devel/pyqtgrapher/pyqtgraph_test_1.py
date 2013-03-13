from PyQt4 import QtCore, QtGui, uic
import pyqtgraph as pg
import numpy as np
import os
from util import color_chooser

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

basepath =  os.path.dirname(__file__)
path = os.path.join(basepath, "qtui","plot_window.ui")
base, form = uic.loadUiType(path)

class PlotWindow(base, form):
    '''
    class for the window consisting of many plots
    '''
    #signal gets called when the user removes a dataset from the plot window
    on_dataset_removed = QtCore.pyqtSignal()
    
    def __init__(self):
        super(PlotWindow, self).__init__()
        #dictionary in the form dataset: [list of plots relating to that dataset]
        self.setupUi(self)
        self.datasets = {}
        self.setup_layout()
        self.connect_layout()
        self.colors = color_chooser()
    
    def new_dataset(self, dataset):
        pass
    
    def new_data(self, dataset, data):
        pass
        
    def new_parameters(self, parameters):
        #if window name is one of these, self.plot_widget.setTitle('first plot!')
        pass    
        
    def setup_layout(self):
        '''
        adds a new plot widget to the layout made in the ui file
        '''
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.addLegend()
        self.hlayout.addWidget(self.plot_widget)
        self.a = self.plot_widget.plot(name = 'another curve')
    
    def connect_layout(self):
        self.spin = QtGui.QSpinBox()
        self.spin.valueChanged.connect(self.on_change)
        self.hlayout.addWidget(self.spin)
    
    def on_change(self, value):
#        self.plot_widget.removeItem(self.a)
        #clear legend
#        print self.plot_widget.plotItem.legend.items
        pen = pg.mkPen(color = self.colors.next_color(), width = 1.0)
        self.plot_widget.plotItem.legend.items = []
        self.a = self.plot_widget.plot(name = 'another curve')
        self.a.setPen(pen)
        self.a.setData(value + np.array([1,2,3,4]), 
                       symbol = 'o', symbolPen = pen, symbolSize = 5.0)

#        self.b = self.a
    
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import common.clients.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    latticeGUI = PlotWindow()
    latticeGUI.setWindowTitle('Grapher')
    latticeGUI.show()
    reactor.run()