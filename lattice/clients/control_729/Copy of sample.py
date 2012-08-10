import sys
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure


class Readout(QtGui.QWidget):
    def __init__(self, parent=None, threshold = 1):
        QtGui.QWidget.__init__(self, parent)
        self.thresholdVal = threshold
        self.create_layout()
    
    def create_layout(self):
        layout = QtGui.QGridLayout()
        plot_layout = self.create_plot_layout()
        layout.addLayout(plot_layout, 0, 0, 1, 4)
        thresholdLabel = QtGui.QLabel("Threshold (Photon Counts Per Readout)")
        binsLabel = QtGui.QLabel("Bins")
        for l in [thresholdLabel, binsLabel]:
            l.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.threshold = QtGui.QSpinBox()
        self.threshold.setKeyboardTracking(False)
        self.threshold.setValue(self.thresholdVal)
        self.bins = QtGui.QSpinBox()
        self.bins.setKeyboardTracking(False)
        self.bins.setValue(50)
        layout.addWidget(thresholdLabel, 1, 0)
        layout.addWidget(self.threshold, 1, 1)
        layout.addWidget(binsLabel, 1, 2)
        layout.addWidget(self.bins, 1, 3)
        self.setLayout(layout)
   
    def create_plot_layout(self):
        layout = QtGui.QVBoxLayout()
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.axes = self.fig.add_subplot(111)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.mpl_toolbar)
        layout.addWidget(self.canvas)
        return layout
    
if __name__ == "__main__":
    app = QtGui.QApplication([])
    form = Readout()
    form.show()
    app.exec_()