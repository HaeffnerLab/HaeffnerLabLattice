"""
### BEGIN NODE INFO
[info]
name = Compensation LineScan
version = 1.0
description = 
instancename = Compensation LineScan

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""


from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import inlineCallbacks, returnValue
import math

SIGNALID = 66060

class compLineScan( LabradServer ):
    """Allows for simple parameterized scanning of the compensation
    The scans are in the form 
    c1 = c1 + r*cos(theta)
    c2 = c2 + r*sin(theta)
    """
    name = 'Compensation LineScan'
    onNewRange = Signal(SIGNALID, 'signal: new range', '(vv)')
    
    def initServer( self ):
        self.setInitialValues()
        self.initializeConnection()
        self.listeners = set()
    
    def setInitialValues(self):
        self.amplitude = 0
        self.angle = 0
        self.angleRange = (-90, 90)
        self.amplitudeRange = (None,None)
        
    @inlineCallbacks
    def initializeConnection(self):
        self.server = self.client.compensation_box
        self.rangec1 = yield self.server.getrange(1)
        self.rangec2 = yield self.server.getrange(2)
        yield self.setAmplitudeRange()

    @inlineCallbacks
    def setAmplitudeRange(self):
        centerc1, centerc2 = yield self.getCenterPosition()
        print 'center', centerc1, centerc2
        maxAmplitude = min(self.rangec1[1] - centerc1, self.rangec2[1] - centerc2)
        minAmplitude = min(self.rangec1[0] - centerc1, self.rangec2[0] - centerc2)
        print 'amplitude', minAmplitude, maxAmplitude
        self.amplitudeRange = (minAmplitude,maxAmplitude)
    
    @inlineCallbacks
    def getCenterPosition(self):
        """Using the current compensation voltages and the current parametrized offset, compute the center of the parametrized offset"""
        c1 = yield self.server.getcomp(1)
        c2 = yield self.server.getcomp(2)
        centerc1 = c1 - self.amplitude * math.cos(self.angle * math.pi / 180.)
        centerc2 = c2 - self.amplitude * math.sin(self.angle * math.pi / 180.)
        returnValue( (centerc1,centerc2) )

    @setting(0, "Get Angle Range", returns='(vv)')
    def getAngleRange(self, c):
        '''Returns the angle of the parameterized line'''
        return self.angleRange
    
    @setting(1, "Get Amplitude Range", returns='(vv)')
    def getAmplitudeRange(self, c):
        '''Returns the range parameter r of the parameterized line'''
        return self.amplitudeRange
    
    @setting(2, "Get Angle", returns='v')
    def getAngle(self, c):
        '''Returns the angle of the parameterized line'''
        return self.angle
    
    @setting(3, "Get Amplitude", returns='v')
    def getAmplitude(self, c):
        '''Returns the parameter r of the parameterized line'''
        return self.amplitude
    
    @setting(4, "Set Angle", angle = 'v',returns = '')
    def setAngle(self, c, angle):
        '''Sets the angle for the parameterized line scan'''
        if not self.angleRange[0] <= angle <= self.angleRange[1]: raise Exception ("Incorrect Angle")
        (centerc1,centerc2) = yield self.getCenterPosition()
        newc1 = centerc1 + self.amplitude * math.cos(angle * math.pi / 180.)
        newc2 = centerc2 + self.amplitude * math.sin(angle * math.pi / 180.)
        yield self.server.setcomp(1, newc1)
        yield self.server.setcomp(2, newc2)
        self.angle = angle
        self.setAmplitudeRange()
        self.onNewRange( self.amplitudeRange, self.listeners )
    
    @setting(5, "Set Amplitude", amplitude = 'v', returns='')
    def setOffset(self, c, amplitude):
        '''Sets the amplitude r of the parameterized line'''
        if not self.amplitudeRange[0] <= amplitude <= self.amplitudeRange[1]: raise Exception ("Incorrect Amplitude")
        (centerc1,centerc2) = yield self.getCenterPosition()
        newc1 = centerc1 + amplitude * math.cos(self.angle * math.pi / 180.)
        newc2 = centerc2 + amplitude * math.sin(self.angle * math.pi / 180.)
        print 'new set', newc1, newc2
        yield self.server.setcomp(1, newc1)
        yield self.server.setcomp(2, newc2)
        self.amplitude = amplitude
        self.setAmplitudeRange()
        self.onNewRange( self.amplitudeRange, self.listeners )

    def initContext(self, c):
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)

if __name__ == "__main__":
    from labrad import util
    util.runServer(compLineScan())
