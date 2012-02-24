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
                   '2':2,
                   '3':3,
                   '4':4,
                   '5':5,
                   '6':6,
                   '7':7,
                   '8':8,
                   '31':31,
                   'testChannel':0
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
        c['sequence'] = Sequence()
    
    @setting(1, "Program Sequence", returns = '')
    def programSequence(self, c, sequence):
        """
        Programs Pulser with the current sequence.
        """
        if self.xem is None: raise('Board not connected')
        sequence = c.get('sequence')
        if not sequence: raise Exception ("Please create new sequence first")
        parsedSequence = sequence.progRepresentation()
        yield self.inCommunication.acquire()
        yield deferToThread(self._programBoard, parsedSequence)    
        self.inCommunication.release()
        self.isProgrammed = True
    
    @setting(2, "Start Infinite", returns = '')
    def startInfinite(self,c):
        if not self.isProgrammed: raise Exception ("No Programmed Sequence")
        yield self.inCommunication.acquire()
        yield deferToThread(self._startInfinite)
        self.inCommunication.release()
    
    @setting(3, "Start", returns = '')
    def start(self, c):
        if not self.isProgrammed: raise Exception ("No Programmed Sequence")
        yield self.inCommunication.acquire()
        yield deferToThread(self._start)
        self.inCommunication.release()
    
    @setting(4, 'Add TTL Pulse', channel = 's', start = 'v', duration = 'v')
    def addTTLPulse(self, c, channel, start, duration):
        """
        Add a TTL Pulse to the sequence, times are in seconds
        """
        hardwareAddr = self.channelDict.get(channel)
        sequence = c.get('sequence')
        #simple error checking
        if hardwareAddr is None: raise Exception("Unknown Channel {}".format(channel))
        if not (MIN_SEQUENCE <= start,start + duration <= MAX_SEQUENCE): raise Exception ("Time boundaries are out of range")
        if not duration >= timeResolution: raise Exception ("Incorrect duration") 
        if not sequence: raise Exception ("Please create new sequence first")
        sequence.addTTLPulse(hardwareAddr, start, duration)
    
    @setting(5, "Human Readable", returns = '*2s')
    def humanReadable(self, c):
        """
        Returns a readable form of the programmed sequence for debugging
        """
        sequence = c.get('sequence')
        if not sequence: raise Exception ("Please create new sequence first")
        ans = sequence.humanRepresentation()
        return ans.tolist()
    
    def _programBoard(self, sequence):
        self.xem.WriteToBlockPipeIn(0x80, 2, sequence)
  
    def _startInfinite(self):
        self.xem.SetWireInValue(0x00,0x03)
        self.xem.UpdateWireIns()
        
    def _start(self):
        self.xem.SetWireInValue(0x00, 0x01)
        self.xem.UpdateWireIns()
    
    ####
    def _reset(self):
        xem.SetWireInValue(0x00, 0x00)
        xem.UpdateWireIns()
            
            
            
class Sequence():
    """Sequence for programming pulses"""
    def __init__(self):
        self.switchingTimes = {} 
        #dictionary in the form time:which channels to swtich
        #time is expressed a timestep with the given resolution
        #which channels to switch is a channelTotal-long with 1 to switch ON, -1 to switch OFF, 0 to do nothing
    
    def addTTLPulse(self, channel, start, duration):
        """adding TTL pulse, times are in seconds"""
        self._addNewSwitch(start, channel, 1)
        self._addNewSwitch(start + duration, channel, -1)

    def secToStep(self, sec):
        '''converts seconds to time steps'''
        return int( sec / timeResolution) 
    
    def numToHex(self, number):
        '''converts the number to the hex representation for a total of 32 bits
        i.e: 3 -> 00000000...000100 ->  \x00\x00\x03\x00, note that the order of 8bit pieces is switched'''
        a,b = number // 65536, number % 65536
        return str(numpy.uint16([a,b]).data)

    def _addNewSwitch(self, t, chan, value):
        timeStep = self.secToStep(t)
        if self.switchingTimes.has_key(timeStep):
            if self.switchingTimes[timeStep][chan]: raise Exception ('Double switch at time {} for channel {}'.format(t, chan))
            self.switchingTimes[timeStep][chan] = value
        else:
            self.switchingTimes[timeStep] = numpy.zeros(channelTotal, dtype = numpy.int8)
            self.switchingTimes[timeStep][chan] = value
           
    def progRepresentation(self):
        """Returns the representation of the sequence for programming the FPGA"""
        rep = ''
        lastChannels = numpy.zeros(channelTotal)
        powerArray = 2**numpy.arange(channelTotal, dtype = numpy.uint64)
        for key,newChannels in sorted(self.switchingTimes.iteritems()):
            channels = lastChannels + newChannels #computes the action of switching on the state
            if (channels < 0).any(): raise Exception ('Trying to switch off channel that is not already on')
            channelInt = numpy.dot(channels,powerArray)
            rep = rep + self.numToHex(key) + self.numToHex(channelInt) #converts the new state to hex and adds it to the sequence
            lastChannels = channels
        rep = rep + 2*self.numToHex(0) #adding termination
        return rep
    
    def humanRepresentation(self):
        """Returns the human readable version of the sequence for FPGA for debugging"""
        rep = self.progRepresentation()
        arr = numpy.fromstring(rep, dtype = numpy.uint16) #does the decoding from the string
        arr = numpy.array(arr, dtype = numpy.uint32) #once decoded, need to be able to manipulate large number
        arr = arr.reshape(-1,4)
        times =( 65536  *  arr[:,0] + arr[:,1]) * timeResolution
        channels = ( 65536  *  arr[:,2] + arr[:,3])
        
        def expandChannel(ch):
            '''function for getting the binary representation, i.e 2**32 is 1000...0'''
            return bin(ch)[2:].zfill(32)
        
        channels = map(expandChannel,channels)
        return numpy.vstack((times,channels)).transpose()
     
if __name__ == "__main__":
    from labrad import util
    util.runServer( Pulser() )