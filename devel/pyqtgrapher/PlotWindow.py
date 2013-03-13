from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
from DatasetList import DatasetList
from util import color_chooser

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class dataset_info(object):
    '''stores information about the dataset'''
    plot_item = None
    legend_items = None
    
class PlotWindow(QtGui.QWidget):
    '''
    class for the window consisting of many plots
    '''
    #signal gets called when the user removes a dataset from the plot window
    on_dataset_removed = QtCore.pyqtSignal()
    
    def __init__(self):
        super(PlotWindow, self).__init__()
        #dictionary in the form dataset_name: dataset_info
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
        layout = QtGui.QHBoxLayout()
        self.dataset_list = DatasetList()
        layout.addWidget(self.dataset_list)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.addLegend()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
    
    def user_dataset_checked(self, dataset, isChecked):
        if not isChecked:
            self.hide_dataset(dataset)
        else:
            self.unhide_dataset(dataset)
    
    def hide_dataset(self, dataset):
        dataset = str(dataset)
        dataset_info = self.datasets[dataset]
        self.plot_widget.removeItem(dataset_info.plot_item)
        self.plot_widget.plotItem.legend.items = []
        dataset_info.legend_items = []
#        for legend_item in dataset_info.legend_items:
#            self.plot_widget.plotItem.legend.items.remove(legend_item)
    
    def unhide_dataset(self, dataset):
        dataset = str(dataset)
        dataset_info = self.datasets[dataset]
        self.plot_widget.addItem(dataset_info.plot_item)
    
    def connect_layout(self):
        self.dataset_list.on_dataset_checked.connect(self.user_dataset_checked)
        
        self.spin = QtGui.QSpinBox()
        self.spin.valueChanged.connect(self.on_change)
        self.layout().addWidget(self.spin)
        
    
    def on_change(self, value):
#        self.plot_widget.removeItem(self.a)
        #clear legend
        s = set(self.plot_widget.plotItem.legend.items)
        print s
#        old_legend = set(self.plot_widget.plotItem.legend.items)
        pen = pg.mkPen(color = self.colors.next_color(), width = 1.0)
#        self.plot_widget.plotItem.legend.items = []
        a = self.plot_widget.plot(name = 'another curve ' + str(value))
        a.setPen(pen)
        a.setData(value + np.array([1,2,3,4]), 
                       symbol = 'o', symbolPen = pen, symbolSize = 5.0)
        new_legend = set(self.plot_widget.plotItem.legend.items)
        d = dataset_info()
        d.plot_item = a
        d.legend_items = new_legend - s
        print  d.legend_items
        
        self.datasets[str(value)] = d
        self.dataset_list.add_dataset(str(value))

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