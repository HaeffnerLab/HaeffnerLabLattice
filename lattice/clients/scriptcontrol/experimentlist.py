'''
Experiment List Widget
'''
from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtCore, QtGui
import numpy as np

class ExperimentListWidget(QtGui.QListWidget):

    def __init__(self, parent):
        QtGui.QListWidget.__init__(self)
        self.parent = parent
        for experiment in self.parent.experiments.keys():
            self.addItem(experiment)
        
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
    def mousePressEvent(self, event):
        """
        mouse clicks events
        """
        button = event.button()
        item = self.itemAt(event.x(), event.y())
        if item:
            if (button == 1):
                self.parent.setupExperimentGrid(str(item.text()))
                self.parent.setupStatusWidget(str(item.text()))
                    



