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
        self.positionDict = {
                            '2':                                  [-.62996, .62996],
                            '3':                                 [-1.0772, 0, 1.0772],
                            '4':                          [-1.4368, -.45438, .45438, 1.4368],
                            '5':                         [-1.7429, -0.8221, 0, 0.8221, 1.7429],
                            '6':                  [-2.0123, -1.4129, -.36992, .36992, 1.4129, 2.0123],
                            '7':                 [-2.2545, -1.1429, -.68694, 0, .68694, 1.1429, 2.2545],
                            '8':           [-2.4758, -1.6621, -.96701, -.31802, .31802, .96701, 1.6621, 2.4758],
                            '9':         [-2.6803, -1.8897, -1.2195, -.59958, 0, .59958, 1.2195, 1.8897, 2.6803],
                            '10': [-2.8708, -2.10003, -1.4504, -.85378, -.2821, .2821, .85378, 1.4504, 2.10003, 2.8708]
                            }
        self.changeDirectory(['', 'Experiments', 'IonSwap'])        
        

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
#        print 'dataset: ', dataset
#        print 'directory: ', self.currentDirectory
        dv = self.parent.parent.cxn.data_vault
        dir = yield dv.cd(self.currentDirectory)
#        print dir
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
            
#            print 'Dimensions: ', hstart, hend, vstart, vend
        except:
            raise Exception('Does this scan have dimension parameters?')
            
        try:
            self.parent.cameraCanvas.updateData(zData, (hend - hstart + 1), (vend - vstart + 1))
        except AttributeError:
            zData = np.reshape(zData, ((self.parent.parent.height + 1), (self.parent.parent.width + 1)))
            self.parent.cameraCanvas.newAxes(zData, hstart, hend, vstart, vend)
            
        # ------ model functions!
        
        #--------------
        
        """ The image, assumed to be have more columns than rows, will first be analyzed
            in the axial direction. The sums of the intensities will be collected in the
            axial direction first. This will help narrow down which section of the image,
            in order to exclude noise.
            
            Example:   |  [[ # # # # # # # # # # # # # # # # # # # # # #],       |
                       0   [ # # # # # # # # # # # # # # # # # # # # # #], avgIonDiameter
                       |   [ # # # # # # # # # # # # # # # # # # # # # #],       |
                      |    [ * * * * * * * * * * * * * * * * * * * * * *], <-- strip of highest intensity,
                      1    [ * * * * * * * * * * * * * * * * * * * * * *], <-- will only be used for 
                      |    [ * * * * * * * * * * * * * * * * * * * * * *], <-- proceeding calculations
                       |   [ % % % % % % % % % % % % % % % % % % % % % %],
                       2   [ % % % % % % % % % % % % % % % % % % % % % %],
                       |   [ % % % % % % % % % % % % % % % % % % % % % %]]
                                  
                                             Axial   
        """
        
        
        rows = (self.parent.parent.height + 1)
        cols = (self.parent.parent.width + 1)
        typicalIonDiameter = self.parent.typIonDiameterSpinBox.value()
        
        axialSumSegments = []
        zData = np.reshape(zData, (rows, cols))
        axialData = np.sum(zData, 1) # 1D vector: sum of intensities in the axial direction. length = rows

        
        """ choose each strip by only analyzing the 1D vector of sums
            
            [ # # # * * * % % %] -> [# * %]
                                     0 1 2
                      ^                ^
                      |                |
                    Segment           most
                                    intense
                                      sum
        """
        intensitySum = 0
        cnt = 0
        for i in np.arange(rows):
            intensitySum += axialData[i]
            cnt += 1
            if (cnt == typicalIonDiameter):
                axialSumSegments.append(intensitySum)
                cnt = 0
                intensitySum = 0 
                
        # find the index of the strip with the highest intensity
        mostIntenseRegionIndex = np.where(axialSumSegments == np.max(axialSumSegments))[0][0]
        
        """ use this strip to create the 1-dimensional array of intensity sums in the radial direction
        
            [ * * * * * * * * * * * * * * * * * * * * * *] 1D vector of sums
                                                            in the radial direction
                                  ^                            length = cols
                                  |                        Used to find peaks
           
           [[ * * * * * * * * * * * * * * * * * * * * * *], most 
            [ * * * * * * * * * * * * * * * * * * * * * *], intense
            [ * * * * * * * * * * * * * * * * * * * * * *]]  strip
            
            
        
        """


        mostIntenseData = zData[(mostIntenseRegionIndex*typicalIonDiameter):(mostIntenseRegionIndex*typicalIonDiameter + typicalIonDiameter), :]
        mostIntenseDataSums = np.sum(mostIntenseData, 0)# / typicalIonDiameter #1D vector
#        mostIntenseDataSums = (mostIntenseDataSums - np.min(mostIntenseDataSums))/(np.max(mostIntenseDataSums) - np.min(mostIntenseDataSums))
        mostIntenseDataSums = mostIntenseDataSums / np.sum(mostIntenseDataSums) # normalized to 1 (divided by the area under the curve)

        
        
        #---------
        
        try:
            
            parameters = yield dv.get_parameter('Parameters')
            parametersArray = []
            for i in parameters:
                parametersArray.append(i.value)
            
    #            print parametersArray
            arrangement = yield dv.get_parameter('Arrangement')
    #            print arrangement
            analysisTime = yield dv.get_parameter('Time')
    #            print analysisTime
            
            positionValues = self.positionDict[str(len(arrangement))]
            
            xmodel = np.arange(cols)
            
            darkModel = 0
            for ion in np.arange(len(arrangement)):
                if arrangement[ion] == 1:
    #                                print ionArrangement, ion
    #                                print positionValues[ion]
                    darkModel += parametersArray[0]*np.exp(-(((xmodel-positionValues[ion]*parametersArray[1] - parametersArray[2])/parametersArray[3])**2)/2)
            
            darkModel += parametersArray[4]
            
            
            if(type(darkModel) != type(np.array([]))):
                darkModel = [parametersArray[4]]*cols 
            
            self.parent.analysisCanvas.drawPlot(dataset, self.currentDirectory[-2], xmodel, mostIntenseDataSums, darkModel, parametersArray, arrangement, analysisTime)
            self.parent.setParametersText(parametersArray)
        
        except:
            xmodel = np.arange(cols)
            self.parent.analysisCanvas.drawPlot(dataset, self.currentDirectory[-2], xmodel, mostIntenseDataSums)

         
                    



