'''
Created on Aug 08, 2011
@author: Michael Ramm, Haeffner Lab
Thanks for some code ideas from Quanta Lab, MIT
'''
import ok
from labrad.server import LabradServer, setting
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, Deferred

#import base64
okDeviceID = 'TimeResolvedCounter'

class TimeResolvedFPGA(LabradServer):
    name = 'TimeResolvedFPGA'
    
    @inlineCallbacks
    def initServer(self):
        self.inRequest = False
        self.singleReadingDeferred = None
        yield Deferred(self.connectOKBoard)
    
    @inlineCallbacks
    """
    Attemps to connect to the OK board with the given okDeviceIDm self.xem = None is not able to connect
    """
    def connectOKBoard(self):
        self.xem = None
        tmp = ok.FrontPanel()
        module_count = tmp.GetDeviceCount()
        print "Found {} modules".format(module_count)
        for serial in ok.GetDeviceListSerial():
            tmp = ok.FrontPanel()
            tmp.OpenBySerial(serial)
            id = tmp.GetDeviceID()
            if id == okDeviceID:
                self.xem = tmp
                print 'Connected to {}'.format(id)
                break
        reactor.callLater(10, self.connectOKBoard)
                
    @setting(0, 'Perform Time Resolved Measurement', timelength = 'v' returns = '')
    """
    Commands to OK board to get ready to peform a single measurement
    The result can then be retrieved with getSingleResult()
    """
    def performSingleReading(self, c, timelength):
        if self.inRequest: raise('Board busy performaing a measurement')
        self.inRequest = True
        self.singleReadingDeferred = Deferred()
        reactor.callLater(0, self.doSingleReading, self.singleReadingDeferred, timelength)
    
    def doSingleReading(self, deferred, timelength):
        self.xem.ActivateTriggerIn(0x40,0) #reset the board
        buf = '\x00'*16776192 ####get this number from timelength, ask hong how
        self.xem.ReadFromBlockPipeOut(0xa0,1024,buf)
        self.inRequest = False
        deferred.callback(buf)
    
    @setting(1, 'Get Result of Measurement', returns = 'v')
    """
    Acquires the result of a single reading requested earlier
    """
    def getSingleResult(self, c):
        if self.singleReadingDeferred is None: raise "Single reading was not previously requested"
        data = yield self.singleReadingDeferred
        self.singleReadingDeferred = None
        returnValue(data)
  
if __name__ == "__main__":
    from labrad import util
    util.runServer( TimeResolvedFPGA() )