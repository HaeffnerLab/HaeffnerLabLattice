'''
Created on Feb 10, 2011

@author: Michael Ramm, christopherreilly
'''

from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
from twisted.internet.defer import Deferred, returnValue
import sys
import time

DEFAULT_SAVE_FOLDER = ['','PMT Counts']
SERVERNAME = 'PMT server'
START_STRING = 's'
STOP_STRING = 'f'
TIMEOUT = 100 #seconds, how long to wait for data
MESSAGELENGTH = 10 #characters

#IMPROVE ON:
#handling of data_vault not found (wait for it to connect)
#exception if serial port times out

class PMTServer(SerialDeviceServer):
    
    name = SERVERNAME
    regKey = 'PMTCounter'
    port = None
    serNode = 'lattice-pc'
    timeout = TIMEOUT
    
    @inlineCallbacks
    def initServer(self):
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
        port = yield self.getPortFromReg( self.regKey )
        self.port = port
        try:
            serStr = yield self.findSerial( self.serNode )
            self.initSerial( serStr, port )
        except SerialConnectionError, e:
            self.ser = None
            if e.code == 0:
                print 'Could not find serial server for node: %s' % self.serNode
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
        try:
            self.dv = self.client.data_vault
            self.dv.cd(DEFAULT_SAVE_FOLDER,True)
            dataset = yield self.dv.new('PMTcounts', [('t', 'num')], [('KiloCounts/sec','866 ON','num'),('KiloCounts/sec','866 OFF','num'),('KiloCounts/sec','Differential Signal','num')])
        except:
            print 'data vault not found'
            raise
        self.createDict(dataset[1])
        self.requestList = []
        self.shouldRun = False
           
    def createDict(self,dataset):
        self.d = {
                  '866ON':0,
                  '866OFF':0,
                  'DIFF':0,
                  'Mode':None,
                  'LastSign':None,
                  'CollectionPeriod':100.0,
                  'DataSet':dataset
                  }
    
            
    @setting( 0, returns = '' )
    def startReceiving( self, c):
        """
        Start receiving counts from the PMT FPGA
        """
        self.checkConnection()
        self.ser.flushinput()
        self.ser.write(STOP_STRING)
        self.ser.write(START_STRING)
        self.shouldRun = True
        reactor.callLater( 0, self.readNewData )

    
    @setting(1, returns = '')
    def stopReceiving(self,c):
        """
        Stop receiving counts from the PMT FPGA
        """
        self.checkConnection()
        self.shouldRun = False
        self.ser.write(STOP_STRING)
        self.ser.flushinput()
        
    @setting(2, count = 'w',returns = '*2v')
    def getNextReadings(self,c, count):
        """
        Gets an array of the new readings of length count
        """
        d = Deferred()
        self.requestList.append(self.readingRequest(d, count))
        data = yield d
        returnValue( data )
    
    class readingRequest():
        def __init__(self, d, count):
            assert count > 0
            self.d = d
            self.count = count
            self.data = []
        
        
    @setting(3, period = 'v', returns ='')
    def setCollectionPeriod(self, c, period ):
        """
        Sets the time period in ms how long the count have been collected.
        Used to output the data in units of Kilocounts / sec.
        """
        assert period > 0
        self.d['CollectionPeriod'] = float(period)
    
    @setting(4, returns = 'v')
    def getCollectionPeriod(self,c):
        """
        Returns the collection period in ms
        """
        return self.d['CollectionPeriod']
    
    @setting(5, returns = 'b')
    def isReceiving(self,c):
        return self.shouldRun
    
    @setting(6, returns = 's')
    def currentDataSet(self,c):
        return self.d['DataSet']
    
    @setting(7, returns = 's')
    def newDataSet(self,c):
        dataset = yield self.dv.new('PMTcounts', [('t', 'num')], [('KiloCounts/sec','866 ON','num'),('KiloCounts/sec','866 OFF','num'),('KiloCounts/sec','Differential Signal','num')])
        self.d['DataSet'] = dataset[1]
        returnValue(self.d['DataSet'])
               
    @inlineCallbacks
    def readNewData(self):
        if self.shouldRun:
            reading = yield self.ser.read(MESSAGELENGTH)
            sign = reading[1]
            count = float(reading[2:11])/self.d['CollectionPeriod']
            if sign not in ['+','-']: print 'PMT SERVER: Wrongly Formatting Packet'
            else:
                self.updateDict(sign, count)
                data = [time.time(),self.d['866ON'],self.d['866OFF'],self.d['DIFF']]
                self.processRequests(data)
                yield self.dv.add(*data)
            reactor.callLater(0,self.readNewData)
    
    def processRequests(self, data):
        for req in self.requestList:
            req.data.append(data)
            if len(req.data) == req.count:
                req.d.callback(req.data)
                self.requestList.remove(req)
                
    def updateDict(self,sign,count):
        assert sign == '+' or sign == '-'
        if sign == self.d['LastSign']:
            #we're in the normal mode
            self.d['Mode'] = 'Normal'
            self.d['866ON'] = count
            self.d['866OFF'] = 0
            self.d['DIFF'] = 0
        else:
            #we're in the differential mode
            self.d['Mode'] = 'Diff'
            if(sign == '-'):
                self.d['866OFF'] = count
            else:
                self.d['866ON'] = count
            self.d['DIFF'] = self.d['866ON'] - self.d['866OFF']
        self.d['LastSign'] = sign
        
if __name__ == "__main__":
    from labrad import util
    util.runServer( PMTServer() )