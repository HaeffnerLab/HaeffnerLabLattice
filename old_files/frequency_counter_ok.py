#Created on Aug 13, 2011
#@author: Michael Ramm, Haeffner Lab
"""
### BEGIN NODE INFO
[info]
name = FreqCounter
version = 1.0
description = 
instancename = FreqCounter

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""


import ok
from labrad.server import LabradServer, setting
from twisted.internet import reactor
from twisted.internet.threads import deferToThread
from twisted.internet.defer import DeferredLock, returnValue
import os
import time

okDeviceID = 'FreqCounter'
devicePollingPeriod = 10

class FreqCounterFPGA(LabradServer):
    name = 'FreqCounter'
    
    def initServer(self):
        self.collectionTime = {0:1.0,1:1.0} #default collection times in the format channel:time(sec)
        self.inCommunication = DeferredLock()
        self.connectOKBoard()
    
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
        path = os.path.join(basepath,'lattice/okfpgaservers/freqcounter.bit')
        prog = xem.ConfigureFPGA(path)
        if prog: raise("Not able to program FPGA")
        pll = ok.PLL22150()
        xem.GetEepromPLL22150Configuration(pll)
        pll.SetDiv1(pll.DivSrc_VCO,4)
        xem.SetPLL22150Configuration(pll)
    
    def _resetFIFO(channel, self):
        if channel == 0:
            self.xem.ActivateTriggerIn(0x40,0)
        elif channel == 1:
            self.xem.ActivateTriggerIn(0x40,1)
        
    def _setUpdateTime(self, channel, time):
        if channel == 0:
            self.xem.SetWireInValue(0x01,int(1000 * time))
        elif channel == 1:
            self.xem.SetWireInValue(0x02,int(1000 * time))
        self.xem.UpdateWireIns()
    
    @setting(0, 'Get Channels', returns = '*w')
    def getChannels(self, c):
        """
        Get Available Channels
        """
        return self.collectionTime.keys()
       
    @setting(1, 'Set Collection Time', channel = 'w', time = 'v', returns = '')
    def setCollectTime(self, c, channel, time):
        """
        Set collection time for the given channel
        """
        time = float(time)
        if not 0.0<time<5.0: raise('incorrect collection time')
        if channel not in self.collectionTime.keys(): raise("Incorrect channel")
        self.collectionTime[channel] = time
        yield self.inCommunication.acquire()
        yield deferToThread(self._setUpdateTime, channel, time)
        self.inCommunication.release()

    @setting(2, 'Reset FIFO', channel = 'w', returns = '')
    def resetFIFO(self,c, channel):
        """
        Resets the FIFO on board, deleting all queued counts
        """
        if channel not in self.collectionTime.keys(): raise("Incorrect channel")
        yield self.inCommunication.acquire()
        yield deferToThread(self._resetFIFO, channel)
        self.inCommunication.release()
    
    @setting(3, 'Get All Counts', channel = 'w', returns = '*(vv)')
    def getALLCounts(self, c, channel):
        """
        Returns the list of counts stored on the FPGA in the form (v1,v2) where v1 is the count rate in Hz
        and v2 is the approximate time of acquisition.
        
        NOTE: For some reason, FGPA ReadFromBlockPipeOut never time outs, so can not implement requesting more packets than
        currently stored because it may hang the device.
        """
        if channel not in self.collectionTime.keys(): raise("Incorrect channel")
        yield self.inCommunication.acquire()
        countlist = yield deferToThread(self.doGetAllCounts, channel)
        self.inCommunication.release()
        returnValue(countlist)
        
    def doGetAllCounts(self, channel):
        inFIFO = self._countsInFIFO(channel)
        reading = self._readCounts(channel, inFIFO)
        split = self.split_len(reading, 4)
        countlist = map(self.infoFromBuf, split)
        countlist = self.convertHz(channel, countlist)
        countlist = self.appendTimes(channel, countlist, time.time())
        return countlist
    
    def convertHz(self, channel, rawCounts):
        Hz = []
        for rawCount in rawCounts:
            Hz.append(float(rawCount) / self.collectionTime[channel])
        return Hz
        
    def appendTimes(self, channel, list, timeLast):
        "appends the collection times to the list using the last known time"
        collectionTime = self.collectionTime[channel]
        for i in range(len(list)):
            count = list[-i-1]
            list[-i - 1] = (count, timeLast - i * collectionTime) 
        print list
        return list
        
    def split_len(self,seq, length):
        #useful for splitting a string in length-long pieces
        return [seq[i:i+length] for i in range(0, len(seq), length)]
    
    def _countsInFIFO(self, channel):
        """
        returns how many counts are in FIFO
        """
        self.xem.UpdateWireOuts()
        if channel == 0:
            inFIFO16bit = self.xem.GetWireOutValue(0x21)
        elif channel == 1:
            inFIFO16bit = self.xem.GetWireOutValue(0x22)
        counts = inFIFO16bit / 2
        return counts
    
    def _readCounts(self, channel, number):
        """
        reads the next number of counts from the FPGA
        """
        buf = "\x00"* ( number * 4 )
        if channel == 0:
            self.xem.ReadFromBlockPipeOut(0xa0,4,buf)
        elif channel == 1:
            self.xem.ReadFromBlockPipeOut(0xa1,4,buf)
        return buf
    
    @staticmethod
    def infoFromBuf(buf):
        #converts the received buffer into useful information
        #the most significant digit of the buffer indicates wheter 866 is on or off
        count = 65536*(256*ord(buf[1])+ord(buf[0]))+(256*ord(buf[3])+ord(buf[2]))
        return count

  
if __name__ == "__main__":
    from labrad import util
    util.runServer( FreqCounterFPGA() )