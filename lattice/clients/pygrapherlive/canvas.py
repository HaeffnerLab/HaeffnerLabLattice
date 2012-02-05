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

'''

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

SCALEFACTOR = 1.5
SCROLLFRACTION = .95; # Data reaches this much of the screen before auto-scroll takes place
INDEPENDENT = 0
DEPENDENT = 1
PLOTS = 2


class Qt4MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self, parent, appWindowParent):    
        # instantiate figure
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        self.appWindowParent = appWindowParent      
        self.cnt = 0
        self.dataDict = {}
        self.plotDict = {}
        self.data = None 
        # create plot 
        self.ax = self.fig.add_subplot(111)
        self.ax.grid()
        self.ax.set_ylim(-1, 100)
        self.ax.set_autoscale_on(False) # disable figure-wide autoscale
        #self.draw()
                
        self.background = self.copy_from_bbox(self.ax.bbox)
    
    # Initialize a place in the dictionary for the dataset
    def initializeDataset(self, dataset, directory):
        self.dataDict[dataset, directory] = None
   
    # retrieve and store the new data from Connections
    def setPlotData(self, dataset, directory, data):
        if (self.dataDict[dataset, directory] == None):# first iteration
            self.dataDict[dataset, directory] = data
            NumberOfDependentVariables = data.shape[1] - 1 # total number of variables minus the independent variable
            # find the smallest x value, this will be the left boundary
            self.initialxmin = data.transpose()[INDEPENDENT][0]
            # set up independent axis, dependent axes for data, and dependent axes for plot
            # a.k.a independent variable, dependent variables, plots
            self.plotDict[dataset, directory] = [[], [[]]*NumberOfDependentVariables, [[]]*NumberOfDependentVariables]
            # cycle through the number of dependent variables and create a line for each
            for i in range(NumberOfDependentVariables):
                label = 'y: ' + str(i)
                self.plotDict[dataset, directory][2][i] = self.ax.plot(self.plotDict[dataset, directory][INDEPENDENT],self.plotDict[dataset, directory][DEPENDENT][i],label = label,animated=True)
            self.ax.legend()
            self.draw()
        else:
            # append the new data
            self.dataDict[dataset, directory] = np.append(self.dataDict[dataset, directory], data, 0) 
    
    # plot the data
    def drawPlot(self, dataset, directory):
        
        data = self.dataDict[dataset, directory]
        
        # note: this will work for slow datasets, need to make sure...
        #...self.plotDict[dataset][1] is not an empty set 
        
        if (data != None):
         
            NumberOfDependentVariables = data.shape[1] - 1 # total number of variables minus the independent variable

            # update the data points
            self.plotDict[dataset, directory][INDEPENDENT] = data.transpose()[INDEPENDENT]
            for i in range(NumberOfDependentVariables):
                self.plotDict[dataset, directory][DEPENDENT][i] = data.transpose()[i+1] # (i + 1) -> in data, the y axes start with the second column
    
            # Reassign dependent axis to smaller integers (in order to fit on screen)
            #self.plotDict[dataset, directory][0] = np.arange(self.plotDict[dataset, directory][0].size)
                               
            # finds the maximum independent variable value
            self.maxX = self.plotDict[dataset, directory][INDEPENDENT][-1]
            
            # flatten the data
            self.plotDict[dataset, directory][PLOTS] = self.flatten(self.plotDict[dataset, directory][2])
            
            # draw the plots onto the canvas and blit them into view
            for i in range(NumberOfDependentVariables):
                self.plotDict[dataset, directory][PLOTS][i].set_data(self.plotDict[dataset, directory][INDEPENDENT],self.plotDict[dataset, directory][DEPENDENT][i])
                self.ax.draw_artist(self.plotDict[dataset, directory][PLOTS][i])
            self.blit(self.ax.bbox)
            
            # check to see if the boundary needs updating
            self.updateBoundary(dataset, directory)
 
    # if the screen has reached the scrollfraction limit, it will update the boundaries
    def updateBoundary(self, dataset, directory):
        current = self.plotDict[dataset, directory][INDEPENDENT][-1]
        xmin, xmax = self.ax.get_xlim()
        xwidth = xmax - xmin
        # if current x position exceeds certain x coordinate, update the screen
        if self.appWindowParent.cb1.isChecked(): 
            if (current > SCROLLFRACTION * xwidth + xmin):
                xmin = current - xwidth/4
                xmax = xmin + xwidth
                self.ax.set_xlim(xmin, xmax)
                self.draw()
        elif self.appWindowParent.cb3.isChecked():
            if (current > SCROLLFRACTION * xwidth + xmin):
                self.autofitData()
        
    # update boundaries to fit all the data and leave room for more               
    def autofitData(self):
        self.ax.set_xlim(self.initialxmin, (SCALEFACTOR*(self.maxX - self.initialxmin) + self.initialxmin))# + .4*(maxX - self.initialxmin))
        self.draw()
    
    # update boundaries to fit all the data                
    def fitData(self):
        maxX = self.maxX
        self.ax.set_xlim(self.initialxmin, maxX)
        self.draw()

    # to flatten lists (for some reason not built in)
    def flatten(self,l):
            out = []
            for item in l:
                    if isinstance(item, (list, tuple)):
                            out.extend(self.flatten(item))
                    else:
                            out.append(item)
            return out