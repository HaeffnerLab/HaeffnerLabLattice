'''
Created on Aug 08, 2011
@author: Michael Ramm, Haeffner Lab
Thanks for code ideas from Quanta Lab, MIT
'''
import ok
import math
from labrad.server import LabradServer, setting
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, Deferred, returnValue
from twisted.internet.threads import deferToThread
import os

#import base64
okDeviceID = 'TimeResolvedFPGA'
ProgramPath = ''
DefaultTimeLength = 0.1 #seconds
devicePollingPeriod = 10
MINBUF,MAXBUF = [1024, 16776192] #range of allowed buffer lengths

class TimeResolvedFPGA(LabradServer):
    name = 'TimeResolvedFPGA'
    
    def initServer(self):
        self.inRequest = False
        self.singleReadingDeferred = None
        self.timelength = DefaultTimeLength
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
        path = os.path.join(basepath,'lattice/devel/okfpgaservers/TimeResolvedFPGA.bit')
        xem.ConfigureFPGA(path)
        pll = ok.PLL22150()
        xem.GetEepromPLL22150Configuration(pll)
        pll.SetDiv1(pll.DivSrc_VCO,4) 
        xem.SetPLL22150Configuration(pll)
    
    @setting(0, "Perform Time Resolved Measurement", timelength = 'v[s]', returns = '')
    def performSingleReading(self, c, timelength = None):
        """
        Commands to OK board to get ready to perform a single measurement
        The result can then be retrieved with getSingleResult()
        """
        if self.xem is None: raise('Board not connected')
        if self.inRequest: raise('Board busy performing a measurement')
        self.inRequest = True
        if timelength is None: timelength = self.timelength
        buflength = self.findBufLength(timelength)
        reactor.callLater(0, self.doSingleReading, buflength)
    
    @inlineCallbacks
    def doSingleReading(self, buflength):
        yield deferToThread(self._singleReading, buflength)

    def _singleReading(self, buflength):
        self.singleReadingDeferred = Deferred()
        self.xem.ActivateTriggerIn(0x40,0) #reset the board
        buf = '\x00'*buflength
        self.xem.ReadFromBlockPipeOut(0xa0,1024,buf)
        self.inRequest = False
        self.singleReadingDeferred.callback(buf)
    
    @staticmethod
    def findBufLength(timelength):
        """
        Converts time length in seconds to length of the buffer needed to request that much data
        Buffer is rounded to 1024 for optimal data transfer rate.
        """
        return (timelength / (40. * 10**-9)) / 1024 * 1024
        
    @setting(1, 'Get Result of Measurement', returns = 's')
    def getSingleResult(self, c):
        """
        Acquires the result of a single reading requested earlier
        """
        if self.singleReadingDeferred is None: raise "Single reading was not previously requested"
        data = yield self.singleReadingDeferred
        self.singleReadingDeferred = None
        returnValue(data)
        
    @setting(2, 'Set Time Length', timelength = 'v[s]', returns = '')
    def setTimeLength(self, c, timelength):
        """
        Sets the default time length for measurements in seconds
        """
        buf = self.findBufLength(timelength)
        if not MINBUF <= buflength <= MAXBUF: raise('Incorrect timelength buffer length out of bounds')
        self.timelength = timelength
  
if __name__ == "__main__":
    from labrad import util
    util.runServer( TimeResolvedFPGA() )