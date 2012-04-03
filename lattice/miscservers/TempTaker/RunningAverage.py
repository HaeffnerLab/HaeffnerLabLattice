import numpy

class RunningAverage():
    """Allows for smoothing of input data by taking a running average"""
    def __init__(self, arrLength, averageNumber):
        self.historyArray = numpy.zeros((averageNumber,arrLength))
        self.averageNumber = averageNumber
        self.counter = 0
        self.filled = False
    
    def add(self, addition):
        self.historyArray[self.counter] = addition 
        self.counter = (self.counter + 1) % self.averageNumber
        if self.counter == 0: self.filled = True
    
    def getAverage(self):
        if self.filled:
            average = numpy.average(self.historyArray, 0)
        else:
            average = numpy.sum(self.historyArray, 0) / self.counter
        return average