from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
from DatasetList import DatasetList
from util import color_chooser

# pg.setConfigOption('background', 'w')
# pg.setConfigOption('foreground', 'k')
pg.functions.USE_WEAVE = False


class dataset_info(object):
    '''stores information about the dataset'''
    plot_data_item = None
    hidden = False
    
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
        self.remove_all_shown()
        dataset_info.hidden = True
        self.add_all_shown()
        
    def remove_all_shown(self):
        for dataset in self.datasets.itervalues():
            if not dataset.hidden:
                self.plot_widget.removeItem(dataset.plot_data_item)
        #clears the legend entirely
        self.plot_widget.plotItem.legend.items = []
    
    def add_all_shown(self):
        for dataset in self.datasets.itervalues():
            if not dataset.hidden:
                self.plot_widget.addItem(dataset.plot_data_item)

    def unhide_dataset(self, dataset):
        dataset = str(dataset)
        dataset_info = self.datasets[dataset]
        self.plot_widget.addItem(dataset_info.plot_data_item)
    
    def connect_layout(self):
        self.dataset_list.on_dataset_checked.connect(self.user_dataset_checked)
        
        self.spin = QtGui.QSpinBox()
        self.spin.valueChanged.connect(self.on_change)
        self.layout().addWidget(self.spin)
        
    
    def on_change(self, value):
#        self.plot_widget.removeItem(self.a)
        #clear legend
#         s = set(self.plot_widget.plotItem.legend.items)
#        old_legend = set(self.plot_widget.plotItem.legend.items)
        pen = pg.mkPen(color = self.colors.next_color(), width = 1.0)
#        self.plot_widget.plotItem.legend.items = []
        new_plot_data_item = self.plot_widget.plot(name = 'another curve ' + str(value))
        new_plot_data_item.setPen(pen)
        new_plot_data_item.setData(value + np.arange(1000), symbol = 'o', symbolSize = 5.0)#,   symbol = 'o', symbolPen = pen)#, 
#                        symbol = 'o', symbolPen = pen, symbolSize = 5.0)
#         new_legend = set(self.plot_widget.plotItem.legend.items)
        d = dataset_info()
        d.plot_data_item = new_plot_data_item
#         d.legend_items = new_legend - s
#         print  d.legend_items
        
        self.datasets[str(value)] = d
        self.dataset_list.add_dataset(str(value))
    
# if __name__=="__main__":
#     a = QtGui.QApplication( [] )
#     import common.clients.qt4reactor as qt4reactor
#     qt4reactor.install()
#     from twisted.internet import reactor
#     latticeGUI = PlotWindow()
#     latticeGUI.setWindowTitle('Grapher')
#     latticeGUI.show()
#     reactor.run()
## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
#     import sys
    a = QtGui.QApplication( [] )
    latticeGUI = PlotWindow()
    latticeGUI.show()
    QtGui.QApplication.instance().exec_()
#     if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#         QtGui.QApplication.instance().exec_()
