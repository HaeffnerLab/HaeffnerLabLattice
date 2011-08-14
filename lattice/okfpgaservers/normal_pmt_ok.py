'''
Created on Aug 13, 2011
@author: Michael Ramm, Haeffner Lab
'''
import ok
from labrad.server import LabradServer, setting
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, Deferred, DeferredLock, returnValue
from twisted.internet.threads import deferToThread
import os
import numpy

okDeviceID = 'NormalPMTCountFPGA'
#DefaultTimeLength = 0.1 #seconds
#devicePollingPeriod = 10
#MINBUF,MAXBUF = [1024, 16776192] #range of allowed buffer lengths
#timeResolution = 5.0*10**-9 #seconds

class TimeResolvedFPGA(LabradServer):
    name = 'NormalPMTCountFPGA'
    
    def initServer(self):
        self.modesAvailable = ['Normal','Differential']
        self.currentMode = 'Normal'
        self.isRunning = False
        self.inCommunication = DeferredLock()
        self.normalModeUpdateTime = 0.100 #default update time
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
        if mode not in self.modesAvailable: raise("Incorrect mode")
        self.mode = mode
        yield self.inCommunication.acquire()
        if mode == 'Normal':
            #set the mode on the device and set update time for normal mode
            self.xem.SetWireInValue(0x00,0x0000)
            self._setUpdateTime(self.normalModeUpdateTime)
        elif mode == 'Differential':
            self.xem.SetWireInValue(0x00,0x0001)
        self.xem.UpdateWireIns()
        self.inCommunication.release()
    
    @setting(1, 'Set Normal Mode Collection Time', time = 'v[s]', returns = '')
    def setCollectTime(self, c, time):
        """
        Sets how long to collect photons in the Normal Mode of Operation
        """
        if 0.0<time<5.0: raise('incorrect collection time')
        self.normalModeUpdateTime = time
        yield self.inCommunication.acquire()
        self._setUpdateTime(self.normalModeUpdateTime)
        self.inCommunication.release()
    
    @setting(2, 'Reset FIFO', returns = '')
    def resetFIFO(self,c):
        """
        Resets the FIFO on board, deleting all queued counts
        """
        yield self.inCommunication.acquire()
        self._resetFIFO()
        self.inCommunication.release()
    
    @setting(3, 'Get PMT Counts', returns = '*(wss)')
    def getPMTCounts(self, c):
        """
        Returns the list of counts stores on the FPGA in the form (w,s1,s2) where w is the count
        and s can be 'N' in normal mode or in Differential mode with repump on and 'D' for differential
        mode when repump is off.
        s2 is the time of acquasition
        """
        
    @staticmethod
    def _countsInFIFO():
        """
        returns how many bytes are in FIFO
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
        #the most significant digit of the buffer indicates wheter 866 is on or ff
        count = 65536*(256*ord(buf[1])+ord(buf[0]))+(256*ord(buf[3])+ord(buf[2]))
        if count > 2**31:
            status = '866off'
            count = count % 2**31
        else:
            status = '866on'
        return (count, status)
    
    @inlineCallbacks
    def doSingleReading(self, buflength):
        yield deferToThread(self._singleReading, buflength)

    def _singleReading(self, buflength):
        self.xem.ActivateTriggerIn(0x40,0) #reset the board
        buf = '\x00'*buflength
        self.xem.ReadFromBlockPipeOut(0xa0,1024,buf)
        self.inRequest = False
        self.singleReadingDeferred.callback(buf)

  
if __name__ == "__main__":
    from labrad import util
    util.runServer( TimeResolvedFPGA() )