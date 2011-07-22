'''
Created on Apr 27, 2011
@author: Michael Ramm, Christopher Reilly Haeffner Lab
'''
from twisted.internet.defer import returnValue, inlineCallbacks, Deferred
from labrad.server import LabradServer, setting
from labrad.errors import Error
from twisted.internet.threads import deferToThread
from twisted.internet import reactor
import numpy as np
from processingFunctions import processingFunctions
from datetime import datetime

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
          
    @setting(1, path = '*s', dataset = 's', process='s', followlive = 'b', arguments = '*(s,v)', returns = '**s' )
    def processData(self, c, path, dataset, process, followlive = False, arguments = None):
        """
        Process the data by specifying the path and dataset name in datavault.
        If followlive is selected, any new updates to the selected dataset will be processed on the flu
        Arguements let user change the default processing settings
        """
        if process not in self.processingFunctions.availableProcesses(): raise Error('Process not available')
        readhandle = ContextHandle(self.client, 'data_vault')
        writehandle = ContextHandle(self.client,'data_vault')
        request = Request(path, dataset, process, readhandle, writehandle, followlive, arguments)
        outputInfo = request.getOutputInfo()
        reactor.callLater(0,request.startProcessing)
        return outputInfo
        
    @setting(2, returns = '*s')
    def nameProcesses(self, c):
        """Returns the list of available processes"""
        return self.processingFunctions.availableProcesses()
    
    @setting(3, process = 's', returns = '*(sv)')
    def optionalInputs(self, c, process):
        """Returns a list of tuples of available inputs with the default values for a given process"""
        if process not in self.processingFunctions.availableProcesses(): raise Error('Process not available')
        return self.processingFunctions.availableInputs(process)
        
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
        #close all current contexts with data vault
        #stop processing all the deferred threads
        pass
    
class Request():
    def __init__(self, inputpath, inputdataset, process, readhandle,writehandle, followlive, arguments):
        self.readhandle = readhandle
        self.writehandle = writehandle
        self.inputpath = inputpath
        self.inputdataset = inputdataset
        self.process = process
        self.followlive = followlive
        self.arguments = arguments
        self.outputfile =  inputdataset + ' ' + self.process + ' ' + str(datetime.now())
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
        try:
            yield self.readhandle.call('cd',self.inputpath)
            yield self.readhandle.call('open',self.inputdataset)
            yield self.writehandle.call('cd',*(self.outputpath,True))
        except:
            raise Error('Dataset not found in provided directory') #find a way to get this out to the user
        #start a timer 24 hours
        #connect endprocessing
        if self.followlive:
            yield self.processRepeatedly()
        else:
            yield self.processOnce()
            
    @inlineCallbacks
    def processOnce(self):
        data = yield self.readhandle.call('get')
        if np.size(data):
            print 'processing ' + self.inputdataset
            yield self.processNewData(data)
            print 'done processing'
        else:
            print 'no data in '+ self.inputdataset
        
    @inlineCallbacks
    def processRepeatedly(self):
        data = yield self.readhandle.call('get')
        if np.size(data):
            yield self.processNewData(data)
            reactor.callLater(0, self.processRepeatedly)
        else:
            print 'no new data'
            reactor.callLater(10, self.processRepeatedly)
            
    @inlineCallbacks
    def processNewData(self, newdata):
        yield deferToThread(self.pF.process, *(self.process, newdata, self.arguments))
        if self.pF.newResultReady:
            resultParams = self.pF.getResultParams()
            output = self.pF.returnResult()
            #delete previous dataset here
            print self.outputfile
            a = yield self.writehandle.call('new',self.outputfile, resultParams[0],resultParams[1])#make more general
            print a
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