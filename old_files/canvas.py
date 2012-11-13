'''
The Canvas Widget handles the actual plotting. 

Because the graph requires the entire dataset to plot, new data received from the
Connections is constantly appended to a copy of the dataset. This data is managed in
a dictionary (dataDict) where they are referenced by the dataset number and directory.
The method, drawPlot, uses the dictionary to determine which dataset to plot. 

The lines are animated onto the canvas via the draw_artist and blit methods. The lines
are stored and managed in a dictionary (plotDict). The dataset number and directory will
reference the data points for the independent variables, the data points for the dependent
variables, and the line objects:

    plotDict[dataset, directory] = [x values, y values (possibly multiple sets), plot lines]  
                                        ^                ^                            ^
                                        |                |                            |
                                    INDEPENDENT (0)   DEPENDENT (1)              PLOTS (2)

The x and y values are used to constantly update the plot lines. The grapher then uses
the plot lines to draw the data onto the canvas.

---

Two mechanisms govern how often a plot is drawn. 

1. A main timer cycles constantly updating a counter. When this counter reaches an exact desired number
(such that, for example, 10 counts = 100ms), the plots are drawn. Note: the plots will NOT be drawn when
the counter is larger than the desired number of counts. Every time the axes change (on_draw()), this counter is reset
back to 0 in order to ensure that there is at least a certain amount of time between repeated calls to draw
the plots.

2. New incoming data will automatically redraw the plots. 

'''

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from matplotlib import pyplot
import time
import numpy as np

TIMERREFRESH = 10 #ms
MAXDATASETSIZE = 1000
SCALEFACTOR = 1.5
SCROLLFRACTION = .8; # Data reaches this much of the screen before auto-scroll takes place
INDEPENDENT = 0
DEPENDENT = 1
PLOTS = 2
MAX = 1
MIN = 0
FIRST = 0
SECOND = 1


class Qt4MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self, parent, appWindowParent):    
        # instantiate figure
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        self.appWindowParent = appWindowParent      
#        self.dataDict = {}
        self.datasetLabelsDict = {}
        self.plotDict = {}
        self.data = None 
        self.drawFlag = True
        self.drawCounter = 0
        self.dataIndex = MAXDATASETSIZE
        self.arrayToPlot = 0
        self.dataInitialized = False
        # create plot 
        self.ax = self.fig.add_subplot(111)
        self.ax.grid()
        self.ax.set_autoscale_on(False) # disable figure-wide autoscale
                
        self.background = self.copy_from_bbox(self.ax.bbox)
    
    def closeMe(self):
        print 'closing!'
        pyplot.close(self.fig) 
        
    # Reset the idle counter, since drawing no longer makes the graph idle
    def on_draw(self, event):
        #self.drawFlag = True
        self.drawCounter = 0       
        
        
    # Initialize a place in the dictionary for the dataset
    def initializeDataset(self, dataset, directory, labels):
        #self.dataDict[dataset, directory] = None
        self.plotDict[dataset, directory] = None
        self.datasetLabelsDict[dataset, directory] = labels 
   
    # retrieve and store the new data from Connections
    def setPlotData(self, dataset, directory, data):
        if (self.plotDict[dataset, directory] == None):# first iteration
            #self.dataDict[dataset, directory] = data
            numberOfDependentVariables = data.shape[1] - 1 # total number of variables minus the independent variable
            self.plotDict[dataset, directory] = [[np.zeros([MAXDATASETSIZE]), np.zeros([MAXDATASETSIZE*numberOfDependentVariables]).reshape(numberOfDependentVariables, MAXDATASETSIZE), [[]]*numberOfDependentVariables],[np.zeros([MAXDATASETSIZE]), np.zeros([MAXDATASETSIZE*numberOfDependentVariables]).reshape(numberOfDependentVariables, MAXDATASETSIZE), [[]]*numberOfDependentVariables]]           
            #Process data here!!
            
            
            numberOfDataPoints = data.shape[0]
            
            #print self.plotDict[dataset, directory][FIRST]
            # update the data points
            self.plotDict[dataset, directory][FIRST][INDEPENDENT][self.dataIndex%MAXDATASETSIZE:(self.dataIndex%MAXDATASETSIZE + numberOfDataPoints)] = data.transpose()[INDEPENDENT]            
            print self.plotDict[dataset, directory][FIRST][INDEPENDENT][self.dataIndex%MAXDATASETSIZE:(self.dataIndex%MAXDATASETSIZE + numberOfDataPoints)]
            for i in range(numberOfDependentVariables):
                self.plotDict[dataset, directory][FIRST][DEPENDENT][i][self.dataIndex%MAXDATASETSIZE:(self.dataIndex%MAXDATASETSIZE + numberOfDataPoints)] = data.transpose()[i+1] # (i + 1) -> in data, the y axes start with the second column
                print self.plotDict[dataset, directory][FIRST][DEPENDENT][i][self.dataIndex%MAXDATASETSIZE:(self.dataIndex%MAXDATASETSIZE + numberOfDataPoints)]
            # update points in the second plot dict, offset by half a wavelength :)
            self.plotDict[dataset, directory][SECOND][INDEPENDENT][(self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE:((self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE + numberOfDataPoints)] = data.transpose()[INDEPENDENT]            
            for i in range(numberOfDependentVariables):
                self.plotDict[dataset, directory][SECOND][DEPENDENT][i][(self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE:((self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE + numberOfDataPoints)] = data.transpose()[i+1] # (i + 1) -> in data, the y axes start with the second column         
            # move the dataIndex up
            self.dataIndex = self.dataIndex + numberOfDataPoints
                      
                        # set up independent axis, dependent axes for data, and dependent axes for plot
            # a.k.a independent variable, dependent variables, plots
            
            # 1st plotDict
            # cycle through the number of dependent variables and create a line for each
            for i in range(numberOfDependentVariables):
                label = self.datasetLabelsDict[dataset, directory][i]
                # create MAXDATASIZE plot thing here
                self.plotDict[dataset, directory][FIRST][PLOTS][i] = self.ax.plot(self.plotDict[dataset, directory][FIRST][INDEPENDENT],self.plotDict[dataset, directory][FIRST][DEPENDENT][i], label = label,animated=True)#'ko', markersize=2
            self.plotDict[dataset, directory][FIRST][PLOTS] = self.flatten(self.plotDict[dataset, directory][FIRST][PLOTS])

            # 2nd plotDict
            # cycle through the number of dependent variables and create a line for each
            for i in range(numberOfDependentVariables):
                label = self.datasetLabelsDict[dataset, directory][i]
                # create MAXDATASIZE plot thing here
                self.plotDict[dataset, directory][SECOND][PLOTS][i] = self.ax.plot(self.plotDict[dataset, directory][SECOND][INDEPENDENT],self.plotDict[dataset, directory][SECOND][DEPENDENT][i], label = label,animated=True)#'ko', markersize=2
            self.plotDict[dataset, directory][SECOND][PLOTS] = self.flatten(self.plotDict[dataset, directory][SECOND][PLOTS])


#            for i in range(numberOfDependentVariables):
#                self.plotDict[dataset, directory][PLOTS][i].set_linestyle('None')

            # find initial graph limits
            #self.initialxmin, self.initialxmax = self.getDataXLimits()
            #self.ax.set_xlim(self.initialxmin,self.initialxmax)
            #self.initialymin, self.initialymax = self.getDataYLimits()
            #self.ax.set_ylim(self.initialymin,self.initialymax)
            self.drawLegend()
            self.draw()
            self.timer = self.startTimer(TIMERREFRESH)
            self.cidpress = self.mpl_connect('draw_event', self.on_draw)
            #self.drawFlag = True
            #self.drawCounter = 0
            self.dataInitialized = True
            self.drawGraph()
        else:
            # ok this is harder cus you gotta be aware of indecies
            # self.dataIndex = self.dataIndex + 
            numberOfDependentVariables = data.shape[1] - 1
            numberOfDataPoints = data.shape[0]

            def setPoints(self, newData, newNumberOfDataPoints):
    
                #print (self.dataIndex%MAXDATASETSIZE + numberOfDataPoints), ' vs. ', MAXDATASETSIZE/2 
                if (((self.dataIndex%MAXDATASETSIZE + numberOfDataPoints) > MAXDATASETSIZE/2) and (self.dataIndex%MAXDATASETSIZE <= MAXDATASETSIZE/2)):
                    print 'I happened 1'
    #                print self.plotDict[dataset, directory][FIRST][INDEPENDENT]
    #                print self.plotDict[dataset, directory][SECOND][INDEPENDENT]
                    if (self.arrayToPlot == 0):
                        self.arrayToPlot = 1
                    else:
                        self.arrayToPlot = 0  
                elif ((((self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE + numberOfDataPoints) > MAXDATASETSIZE/2) and ((self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE <= MAXDATASETSIZE/2)):
                    print 'I happened 2'
    #                print self.plotDict[dataset, directory][FIRST][INDEPENDENT]
    #                print self.plotDict[dataset, directory][SECOND][INDEPENDENT]
                    if (self.arrayToPlot == 0):
                        self.arrayToPlot = 1
                    else:
                        self.arrayToPlot = 0 
    
    
#                print self.plotDict[dataset, directory][FIRST][INDEPENDENT]
#                print self.plotDict[dataset, directory][SECOND][INDEPENDENT]
    
    
                # update the data points
                self.plotDict[dataset, directory][FIRST][INDEPENDENT][self.dataIndex%MAXDATASETSIZE:(self.dataIndex%MAXDATASETSIZE + newNumberOfDataPoints)] = newData.transpose()[INDEPENDENT]            
                for i in range(numberOfDependentVariables):
                    self.plotDict[dataset, directory][FIRST][DEPENDENT][i][self.dataIndex%MAXDATASETSIZE:(self.dataIndex%MAXDATASETSIZE + newNumberOfDataPoints)] = newData.transpose()[i+1] # (i + 1) -> in data, the y axes start with the second column
                # update points in the second plot dict, offset by half a wavelength :)
                self.plotDict[dataset, directory][SECOND][INDEPENDENT][(self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE:((self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE + newNumberOfDataPoints)] = newData.transpose()[INDEPENDENT]            
                for i in range(numberOfDependentVariables):
                    self.plotDict[dataset, directory][SECOND][DEPENDENT][i][(self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE:((self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE + newNumberOfDataPoints)] = newData.transpose()[i+1] # (i + 1) -> in data, the y axes start with the second column         
                # move the dataIndex up
                self.dataIndex = self.dataIndex + newNumberOfDataPoints

            # if you're going to go over the array size, split up the data to avoid it
#            print 'why?: ', (self.dataIndex%MAXDATASETSIZE + numberOfDataPoints),' vs ', MAXDATASETSIZE
#            print 'tubes: ', ((self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE%MAXDATASETSIZE + numberOfDataPoints),' vs ', MAXDATASETSIZE
            if ((self.dataIndex%MAXDATASETSIZE + numberOfDataPoints) > MAXDATASETSIZE):
#                print 'AHHHHHHHHHHHHHHHHHHHH THATS A WARCRY!! 1'
#                # split it up
#                print 'number data points'
#                print 'len of data: ', data.shape[0]
#                print 'number data points: ', numberOfDataPoints
#                print 'wrap index: ', (MAXDATASETSIZE - self.dataIndex%MAXDATASETSIZE)
                data1 = data[0:(MAXDATASETSIZE - self.dataIndex%MAXDATASETSIZE)]
#                print 'len of data1: ', data1.shape[0]
                data2 = data[(MAXDATASETSIZE - self.dataIndex%MAXDATASETSIZE):numberOfDataPoints]
#                print 'len of data2: ', data2.shape[0]
                setPoints(self, data1, data1.shape[0])
                setPoints(self, data2, data2.shape[0])
            elif (((self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE + numberOfDataPoints) > MAXDATASETSIZE):
#                print 'AHHHHHHHHHHHHHHHHHHHH THATS A WARCRY!! 2'
                # split it up
#                print 'number data points'
#                print 'len of data: ', data.shape[0]
#                print 'number data points: ', numberOfDataPoints
#                print 'wrap index: ', (MAXDATASETSIZE - (self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE)
                data1 = data[0:(MAXDATASETSIZE - (self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE)]
#                print 'len of data1: ', data1.shape[0]
                data2 = data[(MAXDATASETSIZE - (self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE):numberOfDataPoints]
#                print 'len of data2: ', data2.shape[0]
                setPoints(self, data1, data1.shape[0])
                setPoints(self, data2, data2.shape[0])
                
            else:
                setPoints(self, data, numberOfDataPoints)

            #might not have to do this!!!
            # if it's gonna go over
#            if ((self.dataIndex + numberOfDataPoints) > MAXDATASETSIZE/2):
#                # do wrap around code, and then tell set_data to change its mind.
#                # wrap around requires 2 steps, fill to MAXDATASETSIZE/2, and then reset
#                # ... the index fill the rest in the beginning
#                # keep in mind we're dealing with two arrays, so four operations!
#                
#                self.plotDict[dataset, directory][FIRST][INDEPENDENT][self.dataIndex%MAXDATASETSIZE:MAXDATASETSIZE/2] = data.transpose()[INDEPENDENT][0:(MAXDATASETSIZE/2 - self.dataIndex%MAXDATASETSIZE)]            
#                for i in range(numberOfDependentVariables):
#                    self.plotDict[dataset, directory][FIRST][DEPENDENT][i][self.dataIndex%MAXDATASETSIZE:MAXDATASETSIZE/2] = data.transpose()[i+1][0:(MAXDATASETSIZE/2 - self.dataIndex%MAXDATASETSIZE)] # (i + 1) -> in data, the y axes start with the second column
#                
#                remainder = (MAXDATASETSIZE - self.dataIndex)
#                self.dataIndex = (self.dataIndex + numberOfDataPoints) - MAXDATASETSIZE # reset self.dataIndex to something small again
#                
#                
#                self.plotDict[dataset, directory][FIRST][INDEPENDENT][0:self.dataIndex] = data.transpose()[INDEPENDENT][remainder:numberOfDataPoints]            
#                for i in range(numberOfDependentVariables):
#                    self.plotDict[dataset, directory][FIRST][DEPENDENT][i][0:self.dataIndex] = data.transpose()[i+1][remainder:numberOfDataPoints] # (i + 1) -> in data, the y axes start with the second column
#                
#                
#
#            # if not
#            else:
#                # update the data points
#                self.plotDict[FIRST][dataset, directory][INDEPENDENT][self.dataIndex%MAXDATASETSIZE:(self.dataIndex%MAXDATASETSIZE + numberOfDataPoints)] = data.transpose()[INDEPENDENT]            
#                for i in range(numberOfDependentVariables):
#                    self.plotDict[FIRST][dataset, directory][DEPENDENT][i][self.dataIndex%MAXDATASETSIZE:(self.dataIndex%MAXDATASETSIZE + numberOfDataPoints)] = data.transpose()[i+1] # (i + 1) -> in data, the y axes start with the second column
#                # update points in the second plot dict, offset by half a wavelength :)
#                self.plotDict[SECOND][dataset, directory][INDEPENDENT][(self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE:((self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE + numberOfDataPoints)] = data.transpose()[INDEPENDENT]            
#                for i in range(numberOfDependentVariables):
#                    self.plotDict[SECOND][dataset, directory][DEPENDENT][i][(self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE:((self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE + numberOfDataPoints)] = data.transpose()[i+1] # (i + 1) -> in data, the y axes start with the second column         
#                # move the dataIndex up
#                self.dataIndex = self.dataIndex + numberOfDataPoints
#
#
#                
#                # wrap data around procedure
#                # the idea is you have to add the data from less than maxdatasetsize to maxdatasetsize
#                # and then add the data from 0 to whatever spilled over maxdatasetsize. 
#                # Keep in mind that the index for "data", and self.dataIndex are totally different (data is smaller by far at this point)
#                
#                
#                # data wraps around
##                self.plotDict[dataset, directory][INDEPENDENT][self.dataIndex:MAXDATASETSIZE] = data.transpose()[INDEPENDENT][0:(MAXDATASETSIZE - self.dataIndex)]            
##                for i in range(numberOfDependentVariables):
##                    self.plotDict[dataset, directory][DEPENDENT][i][self.dataIndex:MAXDATASETSIZE] = data.transpose()[i+1][0:(MAXDATASETSIZE - self.dataIndex)] # (i + 1) -> in data, the y axes start with the second column
##                
##                remainder = (MAXDATASETSIZE - self.dataIndex)
##                self.dataIndex = (self.dataIndex + numberOfDataPoints) - MAXDATASETSIZE # reset self.dataIndex to something small again
##                
##                
##                self.plotDict[dataset, directory][INDEPENDENT][0:self.dataIndex] = data.transpose()[INDEPENDENT][remainder:numberOfDataPoints]            
##                for i in range(numberOfDependentVariables):
##                    self.plotDict[dataset, directory][DEPENDENT][i][0:self.dataIndex] = data.transpose()[i+1][remainder:numberOfDataPoints] # (i + 1) -> in data, the y axes start with the second column
#                
#                # copy the second half of the dataset to the first half
#                print self.dataIndex
#                self.plotDict[dataset, directory][INDEPENDENT][0:(self.dataIndex - MAXDATASETSIZE)] = self.plotDict[dataset, directory][INDEPENDENT][MAXDATASETSIZE:self.dataIndex]            
#                for i in range(numberOfDependentVariables):
#                    self.plotDict[dataset, directory][DEPENDENT][i][0:(self.dataIndex - MAXDATASETSIZE)] = self.plotDict[dataset, directory][DEPENDENT][i][MAXDATASETSIZE:self.dataIndex] # (i + 1) -> in data, the y axes start with the second column
#                self.dataIndex = self.dataIndex - MAXDATASETSIZE
#                # now just add as usual, but the dataIndex has to be reset
#                self.plotDict[dataset, directory][INDEPENDENT][self.dataIndex:(self.dataIndex + numberOfDataPoints)] = data.transpose()[INDEPENDENT]            
#                for i in range(numberOfDependentVariables):
#                    self.plotDict[dataset, directory][DEPENDENT][i][self.dataIndex:(self.dataIndex + numberOfDataPoints)] = data.transpose()[i+1] # (i + 1) -> in data, the y axes start with the second column


                
                # COME BACK HERE AND FIX INITIALXMIN!!
                
                #self.initialxmin = self.plotDict[dataset, directory].transpose()[INDEPENDENT][self.dataIndex] # new minimum?
           
                
#            if self.appWindowParent.datasetCheckboxes[dataset, directory].isChecked():
            self.drawGraph()
    
    def timerEvent(self, evt):
#        print 'canvas timer event'
        self.drawCounter = self.drawCounter + 1
        if (self.drawCounter == 10): #100ms
            self.drawGraph()
#        self.drawGraph()
#        if (self.drawFlag == True):
#            self.drawFlag = False
#            self.drawGraph()
    
    def endTimer(self):
        self.killTimer(self.timer)
       
    def drawLegend(self):
#        handles, labels = self.ax.get_legend_handles_labels()
        handles = []
        labels = []
        for dataset,directory in self.appWindowParent.datasetCheckboxes.keys():
            if self.appWindowParent.datasetCheckboxes[dataset, directory].isChecked():
                for i in self.plotDict[dataset, directory][FIRST][PLOTS]:
                    handles.append(i)
                    labels.append(str(dataset) + ' - ' + i.get_label())
        self.ax.legend(handles, labels)
    
    def drawGraph(self):
#        tstartupdate = time.clock()
        for dataset, directory in self.plotDict:
            # if dataset is intended to be drawn (a checkbox governs this)
            if self.appWindowParent.datasetCheckboxes[dataset, directory].isChecked():
                self.drawPlot(dataset, directory)
#        tstopupdate = time.clock()
#        print tstopupdate - tstartupdate
    # plot the data
    def drawPlot(self, dataset, directory):#, dataset, directory):
            
        #data = self.dataDict[dataset, directory]
               
        # note: this will work for slow datasets, need to make sure...
        #...self.plotDict[dataset][1] is not an empty set 
#        print self.dataIndex
#        print self.plotDict[dataset, directory][INDEPENDENT][0:self.dataIndex]
#        print self.plotDict[dataset, directory][DEPENDENT][0]
#        print self.plotDict[dataset, directory][DEPENDENT][0][0:self.dataIndex]
#        print self.plotDict[dataset, directory][DEPENDENT][1]
#        print self.plotDict[dataset, directory][DEPENDENT][1][0:self.dataIndex]
#        print self.plotDict[dataset, directory][DEPENDENT][2]
#        print self.plotDict[dataset, directory][DEPENDENT][2][0:self.dataIndex]
        
        if (self.dataInitialized == True):
            tstartupdate = time.clock()
         
#            numberOfDependentVariables = data.shape[1] - 1 # total number of variables minus the independent variable
            numberOfDependentVariables = len(self.plotDict[dataset, directory][self.arrayToPlot][1])
            
#            # update the data points
#            self.plotDict[dataset, directory][INDEPENDENT] = data.transpose()[INDEPENDENT]
#            for i in range(numberOfDependentVariables):
#                self.plotDict[dataset, directory][DEPENDENT][i] = data.transpose()[i+1] # (i + 1) -> in data, the y axes start with the second column
    
            # Reassign dependent axis to smaller integers (in order to fit on screen)
            #self.plotDict[dataset, directory][0] = np.arange(self.plotDict[dataset, directory][0].size)
                               
            # finds the maximum independent variable value
#            self.maxX = self.plotDict[dataset, directory][INDEPENDENT][-1]
#            self.maxX = self.plotDict[dataset, directory][INDEPENDENT][self.dataIndex]
             
            # flatten the data
            self.plotDict[dataset, directory][self.arrayToPlot][PLOTS] = self.flatten(self.plotDict[dataset, directory][self.arrayToPlot][PLOTS])
            
            print 'in drawplot about to set data'
            if (self.arrayToPlot == 0):
                drawRange = self.dataIndex%MAXDATASETSIZE
            else:
                drawRange = (self.dataIndex + MAXDATASETSIZE/2)%MAXDATASETSIZE  
            for i in range(numberOfDependentVariables):
#                print self.dataIndex
#                print self.plotDict[dataset, directory][self.arrayToPlot][INDEPENDENT]
                self.plotDict[dataset, directory][self.arrayToPlot][PLOTS][i].set_data(self.plotDict[dataset, directory][self.arrayToPlot][INDEPENDENT][0:drawRange],self.plotDict[dataset, directory][self.arrayToPlot][DEPENDENT][i][0:drawRange])
                try:
                    self.ax.draw_artist(self.plotDict[dataset, directory][self.arrayToPlot][PLOTS][i])
                except AssertionError:
                    print 'failed to draw!'

            
            
            # draw the plots onto the canvas and blit them into view
#            if (self.maxDataSizeReached == False):
##                print 'in drawplot about to set data'
#                for i in range(numberOfDependentVariables):
##                    print self.dataIndex
##                    print self.plotDict[dataset, directory][INDEPENDENT]
#                    self.plotDict[dataset, directory][PLOTS][i].set_data(self.plotDict[dataset, directory][INDEPENDENT][0:self.dataIndex],self.plotDict[dataset, directory][DEPENDENT][i][0:self.dataIndex])
#                    try:
#                        self.ax.draw_artist(self.plotDict[dataset, directory][PLOTS][i])
#                    except AssertionError:
#                        print 'failed to draw!'
#            else:
#                print 'here, thats why'
##                print self.dataIndex
##                print self.plotDict[dataset, directory][INDEPENDENT]
#                for i in range(numberOfDependentVariables):
#                    self.plotDict[dataset, directory][PLOTS][i].set_data(self.plotDict[dataset, directory][INDEPENDENT][0:self.dataIndex],self.plotDict[dataset, directory][DEPENDENT][i][0:self.dataIndex])
#                    try:
#                        self.ax.draw_artist(self.plotDict[dataset, directory][PLOTS][i])
#                    except AssertionError:
#                        print 'failed to draw!'


            
            self.blit(self.ax.bbox)
            
            # check to see if the boundary needs updating
#            self.updateBoundary(dataset, directory, numberOfDependentVariables)
            
            tstopupdate = time.clock()
#            print tstopupdate - tstartupdate

            # del numberOfDependentVariables

    # if the screen has reached the scrollfraction limit, it will update the boundaries
    def updateBoundary(self, dataset, directory, numberOfDependentVariables):
        
        currentX = self.plotDict[dataset, directory][INDEPENDENT][-1]
        
        # find the current maximum/minimum Y values between all lines 
        currentYmax = None
        currentYmin = None
        for i in range(numberOfDependentVariables):
            if (currentYmax == None):
                currentYmax = self.plotDict[dataset, directory][DEPENDENT][i][-1]
                currentYmin = self.plotDict[dataset, directory][DEPENDENT][i][-1]
            else:
                if (self.plotDict[dataset, directory][DEPENDENT][i][-1] > currentYmax):
                    currentYmax = self.plotDict[dataset, directory][DEPENDENT][i][-1]
                elif ((self.plotDict[dataset, directory][DEPENDENT][i][-1] < currentYmin)):
                    currentYmin = self.plotDict[dataset, directory][DEPENDENT][i][-1]
        
        xmin, xmax = self.ax.get_xlim()
        xwidth = xmax - xmin
        ymin, ymax = self.ax.get_ylim()
        ywidth = ymax - ymin

        # if current x position exceeds certain x coordinate, update the screen
        if self.appWindowParent.cb1.isChecked(): 
            if (currentX > SCROLLFRACTION * xwidth + xmin):
                xmin = currentX - xwidth/4
                xmax = xmin + xwidth
                self.ax.set_xlim(xmin, xmax)
                self.draw()
            
        elif self.appWindowParent.cb3.isChecked():
            if (currentX > SCROLLFRACTION * xwidth + xmin):
                self.autofitDataX(currentX, MAX)
            elif (currentX < (1 - SCROLLFRACTION- .15) * xwidth + xmin): # -.15 since usually data travels right
                self.autofitDataX(currentX, MIN)
         
            if (currentYmax > SCROLLFRACTION * ywidth + ymin):
                self.autofitDataY(currentYmax)
            elif (currentYmin < (1 - SCROLLFRACTION) * ywidth + ymin):
                self.autofitDataY(currentYmin)
        
    def getDataXLimits(self):
        xmin = None
        xmax = None
        for dataset, directory in self.appWindowParent.datasetCheckboxes.keys():
            if self.appWindowParent.datasetCheckboxes[dataset, directory].isChecked():
                for i in self.plotDict[dataset, directory][INDEPENDENT]:
                    if (xmin == None):
                        xmin = i
                        xmax = i
                    else:
                        if i < xmin:
                            xmin = i
                        elif i > xmax:
                            xmax = i        
        return xmin, xmax
    
    def getDataYLimits(self):
        ymin = None
        ymax = None
        for dataset, directory in self.appWindowParent.datasetCheckboxes.keys():
            if self.appWindowParent.datasetCheckboxes[dataset, directory].isChecked():
                for i in range(len(self.plotDict[dataset, directory][DEPENDENT])):
                    for j in self.plotDict[dataset, directory][DEPENDENT][i]:
                        if (ymin == None):
                            ymin = i
                            ymax = i
                        else:
                            if j < ymin:
                                ymin = j
                            elif j > ymax:
                                ymax = j
        return ymin, ymax

    def autofitDataY(self, currentY):
        #ymin, ymax = self.ax.get_ylim()
        ymin, ymax = self.getDataYLimits()
        newminY = (ymax - SCALEFACTOR*(ymax - ymin))
        newmaxY = (SCALEFACTOR*(ymax - ymin) + ymin)
        self.ax.set_ylim(newminY, newmaxY) 
        self.draw()
    
    # update boundaries to fit all the data and leave room for more               
    def autofitDataX(self, currentX, minmax):
        xmin, xmax = self.ax.get_xlim()
        dataxmin, dataxmax = self.getDataXLimits()
        if (minmax == MAX):
            newmaxX = (SCALEFACTOR*(dataxmax - dataxmin) + dataxmin)
            self.ax.set_xlim(dataxmin, newmaxX)
        elif (minmax == MIN):
            newminX = (dataxmax - SCALEFACTOR*(dataxmax - dataxmin))
            self.ax.set_xlim(newminX, dataxmax)
        self.draw()
        
    
    # update boundaries to fit all the data                
    
    def fitData(self):
        xmin, xmax = self.getDataXLimits()
        xwidth = abs(xmax - xmin)
        self.ax.set_xlim(xmin - .1*xwidth, xmax + .1*xwidth)
        ymin, ymax = self.getDataYLimits()
        ywidth = abs(ymax - ymin)
        self.ax.set_ylim(ymin - .1*ywidth, ymax + .1*ywidth)
        self.draw()
        #self.ax.set_xlim(self.initialxmin, self.maxX)
        #self.draw()

    # to flatten lists (for some reason not built in)
    def flatten(self,l):
            out = []
            for item in l:
                    if isinstance(item, (list, tuple)):
                            out.extend(self.flatten(item))
                    else:
                            out.append(item)
            return out