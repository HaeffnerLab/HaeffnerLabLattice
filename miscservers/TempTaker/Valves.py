import numpy

class Valves():
    controlledValves = 6
    controlActionThreshold = numpy.array([2.0,2.0,4.0,3.0,2.0,2.0]); #SRC,SRH,BRC,BRH,LRC,LRH
    hysteresis = numpy.array([22.0,12.0,2.0,7.0,22.0,12.0])
    valveMin = numpy.array([15,45,55,55,35,30])
    valveMax = 255
    
    def __init__(self, serial):
        self.serial = serial
        self.previousSignal = numpy.zeros(self.controlledValves)
        self.previousDirection = numpy.zeros(self.controlledValves)

    def valveSignal(self, signal):
        signal = self.testResponseChange(signal)
        signal = self.testDirectionChange(signal)
        signal = self.enforceLimits(signal)
        self.previousSignal = signal
        return signal
    
    def testResponseChange(self, signal):
        '''test for changes in the response in order to minimize valve motion'''
        notChange =  numpy.abs(signal - self.previousSignal) <  self.ControlActionThreshold
        signal[notChange] =  self.previousSignal[notChange]
        signal = signal.round()
        return signal
    
    def testDirectionChange(self, signal):
        direction = numpy.sign(signal - self.previousSignal)
        directionChange = direction != self.previousDirection
        signal[directionChange] = signal + direction * self.hysteresis[directionChange]/2.0
        self.previousDirection = direction
        return signal    
    
    def enforceLimits(self, signal):
        return numpy.clip(signal, self.valveMin, self.valveMax)