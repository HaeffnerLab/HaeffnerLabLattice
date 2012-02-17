import numpy

channelTotal = 32
timeResolution = 20*10**-9
MIN_SEQUENCE = 0
MAX_SEQUENCE = 85 #seconds

class hardwareConfiguration():
    
    channelDict = {
                   '0':0,
                   'testChannel':0,
                   '1':1
                   }

class Sequence():
    """Sequence for programming pulses"""
    def __init__(self):
        self.channelDict = hardwareConfiguration.channelDict
        self.switchingTimes = {0:0} #dictionary in the form time:which channels to swtich
        self.seqEnd = 0
    
    def addTTLPulse(self, channel, start, duration):
        """adding TTL pulse, times are in seconds"""
        if not channel in self.channelDict.keys(): raise Exception("Unknown Channel {}".format(channel))
        if not (MIN_SEQUENCE <= start,start + duration <= MAX_SEQUENCE): raise Exception ("Boundaries are out of range")
        if not duration >= timeResolution: raise Exception ("Incorrect duration") 
        hardwareAddr = self.channelDict[channel]
        for t in [start, start+duration]: self._addNewSwitch(self.secToStep(t), hardwareAddr)
        self.seqEnd = max(self.seqEnd, self.secToStep(start + duration))

    def secToStep(self, sec):
        '''converts seconds to time steps'''
        return int( sec // timeResolution) 
    
    def numToHex(self, number):
        '''converts the number to the hex representation for a total of 32 bits
        i.e: 3 -> 00000000...000100 ->  \x00\x00\x00\x03'''
        a,b = number // 65536, number % 65536
        print str(numpy.uint16([a,b]).data)[0]
        return str(numpy.uint16([a,b]).data)

    def _addNewSwitch(self, time, addr):
        if self.switchingTimes.has_key(time):
            self.switchingTimes[time] += 2**addr
        else:
            self.switchingTimes[time] = 2**addr
    
    def _addLast(self):
        """adds the terminating pulse to the sequence"""
        self._addNewSwitch(self.seqEnd, 0)
        
    def progRepresentation(self):
        """Returns the representation of the sequence for programming the FPGA"""
        self._addLast()
        rep = ''
        for key,channels in sorted(self.switchingTimes.iteritems()):
            rep = rep + self.numToHex(key) + self.numToHex(channels)
        return rep
    
    def humanRepresentation(self):
        """Returns the human version of the sequence for FPGA for debugging"""
        rep = self.progRepresentation()
        return numpy.fromstring(rep, dtype = numpy.uint16)
    
seq = Sequence()
seq.addTTLPulse('testChannel', start = 0, duration = 1e-3)
seq.addTTLPulse('testChannel', start = 1, duration = 1e-3)

import labrad
cxn = labrad.connect()
pulser = cxn.pulser
pulser.program_sequence(seq)

#print seq.switchingTimes
#print seq.humanRepresentation()
##print str(seq.progRepresentation())