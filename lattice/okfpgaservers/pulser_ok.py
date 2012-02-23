#Created on Feb 22, 2012
#@author: Michael Ramm, Haeffner Lab
'''
### BEGIN NODE INFO
[info]
name = Pulser
version = 0.2
description = 
instancename = Pulser

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
'''

import ok
from labrad.server import LabradServer, setting
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.threads import deferToThread
import os
import numpy

okDeviceID = 'Pulser'
devicePollingPeriod = 10

channelTotal = 32
timeResolution = 20*10**-9
MIN_SEQUENCE = 0
MAX_SEQUENCE = 85 #seconds

class hardwareConfiguration():
    channelDict = {
                   '0':0,
                   '1':1,
                   'testChannel':1,
                   '2':2
                   }

class Pulser(LabradServer):
    name = 'Pulser'
    
    def initServer(self):
        self.inCommunication = DeferredLock()
        self.connectOKBoard()
        self.channelDict =  hardwareConfiguration.channelDict
        self.isProgrammed = False
    
    def connectOKBoard(self):
        self.xem = None
        fp = ok.FrontPanel()
        module_count = fp.GetDeviceCount()
        print "Found {} unused modules".format(module_count)
        for i in range(module_count):
            serial = fp.GetDeviceListSerial(i)
            tmp = ok.FrontPanel()
            tmp.OpenBySerial(serial)
            id = tmp.GetDeviceID()
            if id == okDeviceID:
                self.xem = tmp
                print 'Connected to {}'.format(id)
                self.programOKBoard(self.xem)
                return
        print 'Not found {}'.format(okDeviceID)
        print 'Will try again in {} seconds'.format(devicePollingPeriod)
        reactor.callLater(devicePollingPeriod, self.connectOKBoard)
    
    def programOKBoard(self, xem):
        print 'Programming FPGA'
        basepath = os.environ.get('LABRADPATH',None)
        if not basepath:
            raise Exception('Please set your LABRADPATH environment variable')
        path = os.path.join(basepath,'lattice/okfpgaservers/photon.bit')
        prog = xem.ConfigureFPGA(path)
        if prog: raise("Not able to program FPGA")
        pll = ok.PLL22150()
        xem.GetEepromPLL22150Configuration(pll)
        pll.SetDiv1(pll.DivSrc_VCO,4)
        xem.SetPLL22150Configuration(pll)
    
    @setting(0, "New Sequence", returns = '')
    def newSequence(self, c):
        """
        Create New Pulse Sequence
        """
        self.c['sequence'] = Sequence()
    
    @setting(1, "Program Sequence", returns = '')
    def programSequence(self, c, sequence):
        """
        Programs Pulser with the current sequence.
        """
        if self.xem is None: raise('Board not connected')
        sequence = self.c.get('sequence')
        if not sequence: raise Exception ("Please create new sequence first")
        parsedSequence = sequence.progRepresentation()
        yield self.inCommunication.acquire()
        yield deferToThread(self._programBoard, parsedSequence)    
        self.inCommunication.release()
        self.isProgrammed = True
    
    @setting(2, "Start Infinite", returns = '')
    def startInfinite(self,c):
        if not self.isPogrammed: raise Exception ("No Programmed Sequence")
        yield deferToThread(self._startInfinite)
    
    @setting(3, 'Add TTL Pulse', start = 'v', duration = 'v')
    def addTTLPulse(self, channel, start, duration):
        """
        Add a TTL Pulse to the sequence, times are in seconds
        """
        hardwareAddr = self.channelDict.get(channel)
        sequence = self.c.get('sequence')
        #simple error checking
        if not hardwareAddr: raise Exception("Unknown Channel {}".format(channel))
        if not (MIN_SEQUENCE <= start,start + duration <= MAX_SEQUENCE): raise Exception ("Time boundaries are out of range")
        if not duration >= timeResolution: raise Exception ("Incorrect duration") 
        if not sequence: raise Exception ("Please create new sequence first")
        sequence.addTTLPulse(hardwareAddr, start, duration)
    
    def _programBoard(self, sequence):
        self.xem.WriteToBlockPipeIn(0x80, 2, sequence)
  
    def _startInfinite(self):
        self.xem.SetWireInValue(0x00,0x03)
        self.xem.UpdateWireIns()
        
class Sequence():
    """Sequence for programming pulses"""
    def __init__(self):
        self.switchingTimes = {} 
        #dictionary in the form time:which channels to swtich
        #time is expressed a timestep with the given resolution
        #which channels to switch is an integer between 0 and 2**channelTotal 
        #where switching channel 2 on and the rest off would correspond to 2**0 * 0 + 2**1 * 0  + 2**2 * 1 + 0
    
    def addTTLPulse(self, channel, start, duration):
        """adding TTL pulse, times are in seconds"""
        self._addNewSwitch(start, channel, 1)
        self._addNewSwitch(start + duration, channel, 0)

    def secToStep(self, sec):
        '''converts seconds to time steps'''
        return int( sec // timeResolution) 
    
    def numToHex(self, number):
        '''converts the number to the hex representation for a total of 32 bits
        i.e: 3 -> 00000000...000100 ->  \x00\x00\x03\x00, note that the order of 8bit pieces is swtiched'''
        a,b = number // 65536, number % 65536
        return str(numpy.uint16([a,b]).data)

    def _addNewSwitch(self, t, chan, value):
        timeStep = self.secToStep(t)
        if self.switchingTimes.has_key(timeStep):
            self.switchingTimes[timeStep] += value * 2**(chan)
        else:
            self.switchingTimes[timeStep] = value * 2**(chan)
           
    def progRepresentation(self):
        """Returns the representation of the sequence for programming the FPGA"""
        rep = ''
        for key,channels in sorted(self.switchingTimes.iteritems()):
            rep = rep + self.numToHex(key) + self.numToHex(channels)
        rep = rep + 2*self.numToHex(0) #adding termination
        return rep
    
    def humanRepresentation(self):
        """Returns the human version of the sequence for FPGA for debugging"""
        rep = self.progRepresentation()
        return numpy.fromstring(rep, dtype = numpy.uint16)
    
if __name__ == "__main__":
    from labrad import util
    util.runServer( Pulser() )