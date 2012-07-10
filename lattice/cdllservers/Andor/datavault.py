'''
DataVault browser widget
'''
from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtCore, QtGui
import numpy as np

class DataVaultWidget(QtGui.QListWidget):

    def __init__(self, parent, context):
        QtGui.QListWidget.__init__(self)
        self.parent = parent
        self.context = context
        self.setMaximumWidth(250)

    @inlineCallbacks
    def populateList(self):
        self.clear()
        self.currentDirectory = yield self.parent.parent.cxn.data_vault.cd(context = self.context)
        self.currentDirectory = tuple(eval(str(self.currentDirectory)))
        self.addItem(str(self.currentDirectory))
        self.addItem('..')
        self.fileList = yield self.parent.parent.cxn.data_vault.dir(context = self.context)
           
        # add sorted directories
        for i in self.sortDirectories():
            self.addItem(i)
        # add sorted datasets
        for i in self.sortDatasets():
            self.addItem(i)

    def sortDirectories(self):
        self.directories = []
        for i in range(len(self.fileList[0])):
            self.directories.append(self.fileList[0][i])
        if self.directories:
            self.directories.sort()
        return self.directories
    
    def sortDatasets(self):
        self.datasets = []
        for i in range(len(self.fileList[1])):
            self.datasets.append(self.fileList[1][i])
        if self.datasets:
            self.datasets.sort()
        return self.datasets

    def addDatasetItem(self, itemLabel, directory):
        if (directory == self.currentDirectory):
            self.addItem(itemLabel)
    
    @inlineCallbacks
    def changeDirectory(self, directory):
        yield self.parent.parent.cxn.data_vault.cd(directory, context = self.context)
        self.populateList()

    
    def mousePressEvent(self, event):
        """
        mouse clicks events
        """
        button = event.button()
        item = self.itemAt(event.x(), event.y())
        if item:
            if (item == self.item(1)):
                if (button == 1):
                    self.changeDirectory(1)
            elif (str(item.text()) in self.directories):
                # select the item we clicked
                self.setCurrentItem(item)
                if (button == 1):
                    self.changeDirectory(str(item.text()))
            elif (str(item.text()) in self.datasets):
                itemText = item.text()
                dataset = int(str(itemText)[0:5]) # retrieve dataset number
                datasetName = str(itemText)[8:len(itemText)]
                if (button == 1):
                    #try:
                    self.retriveScan(dataset)
                    #except:
                    #    print 'how about clicking on something useful?'

    @inlineCallbacks
    def retriveScan(self, dataset):
        print 'dataset: ', dataset
        print 'directory: ', self.currentDirectory
        dv = self.parent.parent.cxn.data_vault
        dir = yield dv.cd(self.currentDirectory)
        print dir
        yield dv.open(dataset)
        Data = yield dv.get()
        data = Data.asarray
        zData = np.array([None]*len(data), dtype=float)
        for i in np.arange(len(data)):
            zData[i] = int(data[i][2])
        
        try: 
            hstart = yield dv.get_parameter('hstart')
            hend = yield dv.get_parameter('hend')
            vstart = yield dv.get_parameter('vstart')
            vend = yield dv.get_parameter('vend')
            
            print 'Dimensions: ', hstart, hend, vstart, vend
        except:
            raise Exception('Does this scan have dimension parameters?')
            
        try:
            self.parent.cameraCanvas.updateData(zData, (hend - hstart + 1), (vend - vstart + 1))
        except AttributeError:
            zData = np.reshape(zData, ((self.parent.parent.height + 1), (self.parent.parent.width + 1)))
            self.parent.cameraCanvas.newAxes(zData, hstart, hend, vstart, vend)

         
         # send to newAxes                   
                    



