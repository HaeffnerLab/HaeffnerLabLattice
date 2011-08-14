'''
Created on Aug 13, 2011
@author: Michael Ramm, Haeffner Lab
'''
import ok
from labrad.server import LabradServer, setting
from twisted.internet import reactor
from twisted.internet.defer import DeferredLock
import os
import time

okDeviceID = 'NormalPMTCountFPGA'

class TimeResolvedFPGA(LabradServer):
    name = 'NormalPMTCountFPGA'
    
    def initServer(self):
        self.collectionTime = {'Normal':0.100,'Differential':0.100}
        self.currentMode = 'Normal'
        self.inCommunication = DeferredLock()
#        self.normalModeUpdateTime = 0.100 #default update time
#        self.differentialModeUpdateTime = 0.100
        self.connectOKBoard()
    
    def connectOKBoard(self):
        self.xem = None
        fp = ok.FrontPanel()
        module_count = fp.GetDeviceCount()
        print "Found {} modules".format(module_count)
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
        path = os.path.join(basepath,'lattice/okfpgaservers/normal.bit')
        prog = xem.ConfigureFPGA(path)
        if prog: raise("Not able to program FPGA")
        pll = ok.PLL22150()
        xem.GetEepromPLL22150Configuration(pll)
        pll.SetDiv1(pll.DivSrc_VCO,4)
        xem.SetPLL22150Configuration(pll)
    
    @staticmethod
    def _resetFIFO():
        self.xem.ActivateTriggerIn(0x40,0)
    
    @staticmethod
    def _setUpdateTime(time):
        self.xem.SetWireInValue(0x01,int(1000 * time))
      
    @setting(0, 'Set Mode', mode = 's', returns = '')
    def setMode(self, c, mode):
        """
        Set the counting mode, either 'Normal' or 'Differential'
        In the Normal Mode, the FPGA automatically sends the counts with a preset frequency
        In the differential mode, the FPGA uses triggers from Paul's box for the counting
        frequency and to know when the repumping light is swtiched on or off.
        """
        if mode not in self.collectionTime.keys(): raise("Incorrect mode")
        self.mode = mode
        yield self.inCommunication.acquire()
        if mode == 'Normal':
            #set the mode on the device and set update time for normal mode
            self.xem.SetWireInValue(0x00,0x0000)
            self._setUpdateTime(self.collectionTime[mode])
        elif mode == 'Differential':
            self.xem.SetWireInValue(0x00,0x0001)
        self.xem.UpdateWireIns()
        self._resetFIFO()
        self.inCommunication.release()
    
    @setting(1, 'Set Collection Time', time = 'v[s]', mode = 's', returns = '')
    def setCollectTime(self, c, time, mode):
        """
        Sets how long to collect photonslist in either 'Normal' or 'Differential' mode of operation
        """
        if not 0.0<time<5.0: raise('incorrect collection time')
        if mode not in self.collectionTime.keys(): raise("Incorrect mode")
        if mode == 'Normal':
            self.collectionTime[mode] = time
            yield self.inCommunication.acquire()
            self._setUpdateTime(time)
            self.inCommunication.release()
        elif mode == 'Differential':
            self.collectionTime[mode] = time
    
    @setting(2, 'Reset FIFO', returns = '')
    def resetFIFO(self,c):
        """
        Resets the FIFO on board, deleting all queued counts
        """
        yield self.inCommunication.acquire()
        self._resetFIFO()
        self.inCommunication.release()
    
    @setting(3, 'Get All Counts', atleast = 'w',returns = '*(wss)')
    def getALLCounts(self, c, atleast = 0):
        """
        Returns the list of counts stored on the FPGA in the form (w,s1,s2) where w is the count
        and s can be 'ON' in normal mode or in Differential mode with repump on and 'OFF' for differential
        mode when repump is off. s2 is the approximate time of acquasition
        
        The optional atleast parameter determines requires we get back at least that number
        of counts, which may lead to waiting for the next counts if they are not already 
        in the queue
        """
        yield self.inCommunication.acquire()
        inFIFO = yield self._countsInFIFO()
        request = max(inFIFO, atleast)
        reading = yield self._readCounts(request)
        self.inCommunication.release()
        split = self.split_len(reading, 4)
        countlist = map(infoFromBuf, split)
        countlist = map(convertKCperSEC, countlist)
        countlist = self.appendTimes(countlist, time.time())
        returnValue( countlist)    
    
    def convertKCperSec(self, input):
        [rawCount,type] = input
        countKCperSec = float(rawCount) / self.collectionTime[self.currentMode] / 1000.
        return [countKCperSec, type]
        
    def appendTimes(self, list, timeLast):
        #in the case that we received multiple PMT counts, uses the current time
        #and the collectionTime to guess the arrival time of the previous readings
        #i.e ( [[1,2],[2,3]] , timeLAst = 1.0, normalupdatetime = 0.1) ->
        #    ( [(1,2,0.9),(2,3,1.0)])
        collectionTime = self.collectionTime[self.currentMode]
        for i in range(len(list)):
            list[-i - 1].append(timeLast - i * collectionTime)
            list[-i - 1] = tuple(list[-i - 1])
        return list
        
    def split_len(self,seq, length):
        #useful for splitting a string in lenght-long pieces
        return [seq[i:i+length] for i in range(0, len(seq), length)]
    
    @staticmethod
    def _countsInFIFO():
        """
        returns how many counts are in FIFO
        """
        xem.UpdateWireOuts()
        inFIFO16bit = xem.GetWireOutValue(0x21)
        counts = inFIFO16bit / 2
        return counts
    
    @staticmethod
    def _readCounts(number):
        """
        reads the next number of counts from the FPGA
        """
        buf = "\x00"* ( number * 4 )
        xem.ReadFromBlockPipeOut(0xa0,4,buf)
        return buf
    
    @staticmethod
    def infoFromBuf(buf):
        #converts the received buffer into useful information
        #the most significant digit of the buffer indicates wheter 866 is on or off
        count = 65536*(256*ord(buf[1])+ord(buf[0]))+(256*ord(buf[3])+ord(buf[2]))
        if count > 2**31:
            status = 'OFF'
            count = count % 2**31
        else:
            status = 'ON'
        return [count, status]

  
if __name__ == "__main__":
    from labrad import util
    util.runServer( TimeResolvedFPGA() )