'''
Created on Apr 27, 2011
@author: Michael Ramm, Christopher Reilly Haeffner Lab
'''
from twisted.internet.defer import returnValue, inlineCallbacks, Deferred
from labrad.server import LabradServer, setting
from labrad.errors import Error
from twisted.internet.threads import deferToThread
import time
from twisted.internet import reactor
import numpy as np
from processingFunctions import processingFunctions

class dataProcessor( LabradServer ):
    """
    Server for processing raw data from data vault and savings the results back to data vault.
    """
    name = 'dataProcessor'
    def initServer(self):
        try:
            self.dv = self.client.data_vault
        except Exception, e:####
            print 'Need to start data vault'
            self.dv = None
        self.processingFunctions = processingFunctions()
          
    @setting(1, path = '*s', dataset = 's', process='s', returns = '**s' )
    def processData(self, c, path, dataset, process):
        if process not in self.processingFunctions.availableProcesses(): raise Error('Process not available')
        readhandle = ContextHandle(self.client, 'data_vault')
        writehandle = ContextHandle(self.client,'data_vault')
        request = Request(path, dataset, process, readhandle, writehandle)
        outputInfo = request.getOutputInfo()
        reactor.callLater(0,request.startProcessing)
        return outputInfo
        
###        
    def serverConnected( self, ID, name ):
       if name is 'Data Vault':
           self.dv = self.client.data_vault
           print 'Data Vault Connected'
###   
    def serverDisconnected( self, ID, name ):
        if name is 'Data Vault':
            self.dv = None
            print 'Data Vault Disconnected'
###
    def stopServer( self ):
        #close all current contexsts with datavault
        #stop processing all the deferred threads
        pass
    
class Request():

    def __init__(self, inputpath, inputdataset, process, readhandle,writehandle):
        self.readhandle = readhandle
        self.writehandle = writehandle
        self.inputpath = inputpath
        self.inputdataset = inputdataset
        self.process = process
        self.outputfile =  inputdataset + ' ' + self.process
        self.outputpath = inputpath + ['Processed Data']
        self.pF = processingFunctions()
    
    def getOutputInfo(self):
        return [self.outputpath,[self.outputfile]]
    
    def listener(self,msgCtx, data):
        self.newData() 
        
    @inlineCallbacks    
    def startProcessing(self):
        #self.cumulRawData = np.array()
        #self.cumulProcData = np.array()
        yield self.readhandle.call('cd',self.inputpath)
        yield self.readhandle.call('open',self.inputdataset)
        yield self.writehandle.call('cd',*(self.outputpath,True))
        #start a timer 24 hours
        #connect endprocessing
        yield self.newData()
        
    @inlineCallbacks
    def newData(self):
        data = yield self.readhandle.call('get')
        if np.size(data):
            yield self.processNewData(data)
            reactor.callLater(0, self.newData)
        else:
            print 'no new data'
            reactor.callLater(1, self.newData)
            
            
    @inlineCallbacks
    def processNewData(self, newdata):
        print 'processing data'
        yield deferToThread(self.pF.process, *(self.process, newdata))
        if self.pF.newResultReady:
            resultParams = self.pF.getResultParams()
            output = self.pF.returnResult()
            #delete previous dataset here
            yield self.writehandle.call('new',self.outputfile, resultParams[0],resultParams[1])#make more general
            print output
            print np.shape(output)
            yield self.writehandle.call('add',output)
        
class ContextHandle( object ):
    def __init__( self, cxn, server ):
        self.cxn = cxn
        self.context = self.cxn.context()
        self.server = server  

    @inlineCallbacks
    def call( self, setting, *args, **kwargs ):
        kwargs['context'] = self.context
        result = yield self.cxn.servers[self.server].settings[setting]( *args, **kwargs )
        returnValue( result )
        
    
    def addListener( self, listener, ID ):
        self.cxn._addListener( listener = listener, source = None, ID = ID, context = self.context )

    def removeListener( self, listener, ID ):
        self.cxn._removeListener( listener = (listener,(),{}), source = None, ID = ID, context = self.context )


if __name__ == "__main__":
    from labrad import util
    util.runServer( dataProcessor() )