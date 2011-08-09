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

DEFAULT_SAVE_FOLDER = ['','TimeResolvedCounts']
okDeviceID = 'TimeResolvedCounter'

class TimeResolvedServer(LabradServer):
    name = 'Time Resolved Server'
    
    def initServer(self):
        self.connectDataVault()
        self.connectOKBoard()
        self.inRequest = False
    
    
    """
    Tries to connected to data vault, self.dv = None is unable to connect
    """
    def connectDataVault(self):
        try:
            self.dv = self.client.data_vault
            self.dv.cd(DEFAULT_SAVE_FOLDER,True)
        except:
            print 'Data Vault Not Found'
            self.dv = None      
    
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
                
#    def newDataSet(self):
#        dataset = yield self.dv.new('TimeResolvedcounts',['Trial'],['Counts'],'s')
#        #self.createDict(dataset[1])
#        #self.shouldRun = False
#               
#    def createDict(self, dataset):
#        self.d = {
#                  'DataSet':dataset,
#                  'TrialCount':0,
#                  'TotalMessage':''
#                  }
        
    @setting(0, 'Reset the Board', returns = '')
    """
    Resets the board to get it ready for counting
    """
    def reset(self, c):
        if self.xem is None: raise('No Board is connected')
        self.xem.ActivateTriggerIn(0x40,0)
    
    @setting(1, 'Perform Single Reading', timelength = 'v' returns = '')
    """
    Commands to OK board to get ready to peform a single measurement
    The result can then be retrieved with getSingleResult()
    """
    def performSingleReading(self, c, timelength):
        if self.xem is None: raise('No Board is Connected')
        self.singleReadingDeferred = Deferred()
        reactor.callLater(0, self.doSingleReading, self.singleReadingDeferred, timelength)
    
    def doSingleReading(self, deferred, timelength):
        self.xem.ActivateTriggerIn(0x40,0)
        buf = '\x00'*16776192 ####get this number from timelength, ask hong how
        self.xem.ReadFromBlockPipeOut(0xa0,1024,buf)
        deferred.callback(buf)
    
    @setting(2, 'Get Result of Single Reading', returns = 'v')
    """
    Acquires the result of a single reading requested earlier
    """
    def getSingleResult(self, c):
        data = yield self.singleReadingDeferred
        returnValue(data)
            
if __name__ == "__main__":
    from labrad import util
    util.runServer( TimeResolvedServer() )