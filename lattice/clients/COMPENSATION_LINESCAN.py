import sys, os
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
from qtui.QCustomFreqPower import QCustomFreqPower

UpdateTime = 100 #in ms, how often data is checked for communication with the server

class COMPENSATION_LINESCAN_CONTROL(QCustomFreqPower):
    def __init__(self, cxn,parent=None):
        QtGui.QWidget.__init__(self, parent)
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/clients/qtui/compensationlinescan.ui')
        uic.loadUi(path,self)
        self.server = cxn.compensation_box
        self.range = self.server.getRange(1)
        [MinLevel, MaxLevel] = self.range
        self.slider.setRange(100*MinLevel, 100*MaxLevel)
        self.parameter.setRange(MinLevel, MaxLevel)
        self.slope.setRange(0,3)
        self.offset.setRange(-1000,1000) ##deepnds on the slope actually
        #connect functions
        self.slider.valueChanged.connect(self.sliderChanged)
        self.parameter.valueChanged.connect(self.parameterChanged)
        self.offset.valueChanged.connect(self.offsetChanged)
        self.slope.valueChanged.connect(self.slopeChanged)   
        #set initial values
        [slope, offset , parameter] =  self.server.getlinescanvalues()
        self.parameter.setValue(parameter)
        self.offset.setValue(offset)
        self.slope.setValue(slope)
        self.setNewRanges()
        #keeping track of what's been updated
        self.offsetUpdated = False
        self.slopeUpdated = False
        self.parameterUpdated = False
        #start timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
        
    def sliderChanged(self, value):
        self.parameter.setValue(value / 100.)
    
    def parameterChanged(self, value):
        self.slider.setValue(value * 100.)
        self.parameterUpdated = True
    
    def setNewRanges(self):
        [minc1, maxc1] = self.range
        m = self.slope.value()
        offset = self.offset.value()
        minfromc2 = (minc1 - offset) / m
        maxfromc2 = (maxc1 - offset) / m
        minimum = max(minc1,minfromc2) + 5
        maximum = min(maxc1, maxfromc2) - 5
        print minimum,maximum
        self.parameter.setRange(minimum,maximum)
        self.slider.setRange(100*minimum, 100*maximum)
    
        
    def slopeChanged(self):
        self.slopeUpdated = True
    
    def offsetChanged(self):
        self.offsetUpdated = True
	            
    #if inputs are updated by user, send updated values to server
    def sendToServer(self):
        if self.server.updateddifferentcontext():
            print 'line scan updating itself'
            [slope, offset , parameter] =  self.server.getlinescanvalues()
            self.parameter.blockSignals(True)
            self.offset.blockSignals(True)
            self.slope.blockSignals(True)
            self.slider.setValue(parameter * 100)
            self.offset.setValue(offset)
            self.slope.setValue(slope)
            self.parameter.blockSignals(False)
            self.offset.blockSignals(False)
            self.slope.blockSignals(False)
            
        if self.parameterUpdated:
            print 'compensation line scan telling server new info'
            self.server.setlinescanvalue(self.parameter.value())
            self.parameterUpdated = False
            self.setNewRanges()
        if self.offsetUpdated:
            print 'compensation line scan telling server new info'
            self.server.setlinescanoffset(self.offset.value())
            self.offsetUpdated = False
            self.setNewRanges()
        if self.slopeUpdated:
            print 'compensation line scan telling server new info'
            self.server.setlinescanslope(self.slope.value())
            self.slopeUpdated = False
            self.setNewRanges()
    

if __name__=="__main__":
    import labrad
    cxn = labrad.connect()
    app = QtGui.QApplication(sys.argv)
    icon = COMPENSATION_LINESCAN_CONTROL(cxn)
    icon.show()
    app.exec_()