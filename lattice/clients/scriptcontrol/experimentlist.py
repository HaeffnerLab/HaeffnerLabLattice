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
        for experiment in self.parent.experiments:
            self.addItem(experiment)
        
        
    def mousePressEvent(self, event):
        """
        mouse clicks events
        """
        button = event.button()
        item = self.itemAt(event.x(), event.y())
        if item:
            if (button == 1):
                print item.text()
                self.parent.setupExperimentGrid(str(item.text()))

    def newHistogram(self, dataset):
        print 'dataset: ', dataset
        print 'directory: ', self.currentDirectory
        self.parent.newHistogram(dataset, self.currentDirectory)
                    



