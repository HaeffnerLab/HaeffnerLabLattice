'''
Created on Feb 11, 2011

@author: Michael Ramm, christopherreilly
'''
from labrad.server import LabradServer, setting
from twisted.internet import reactor
from twisted.internet.defer import returnValue, inlineCallbacks
import sys
import time
import base64

ADAPTER = 1
DEFAULT_SAVE_FOLDER = ['','FirstRecooling'] #where to save data, unless specified
SERVERNAME = 'Time Resolved Server'
TIMEOUT = 1 #day how long to wait for data
NUMTOCOLLECT = 1000 #number of packets to read in at one time
SOURCEMAC = '00:AA:BB:CC:DD:EE'

#follow improvements from the PMTserver

class TimeResolvedServer(LabradServer):
    
    name = SERVERNAME
    port = None
    serNode = 'lattice-pc'
    timeout = TIMEOUT
    
    def initServer(self):
        try:
            #establish connection with ethernet server
            self.eth = self.client._direct_ethernet
            self.eth.connect(ADAPTER)
            self.eth.require_source_mac(SOURCEMAC)
            self.eth.timeout(1)#sets timeout to 1 DAY, how long collect function waits before it returns error
        except:
            print 'ethernet server not found'
            raise
        try:
            self.dv = self.client.data_vault
            self.dv.cd(DEFAULT_SAVE_FOLDER,True)
            self.dv.new('Recooling',['Trial'],['Counts'],'s')
        except:
            print 'data vault not found'
            raise
        self.createDict()
        #funny way to launch itself
        reactor.callLater(1,self.selflaunch)
        self.count = 0
        self.totalmessage = ''
               
    def selflaunch(self):
        print 'trying to self launch'
        self.s = self.client.time_resolved_server
        self.s.startreceiving()
 
    #will be used to store local information
    def createDict(self):
        pass
            
    @setting( 0, returns = '' )
    def startReceiving( self, c):
        """
        Start receiving counts from the PMT FPGA
        """
        self.eth.clear()
        self.eth.listen()
        self.shouldRun = True
        reactor.callLater( 0, self.readNewData )

    
    @setting(1, returns = '')
    def stopReceiving(self,c):
        """
        Stop receiving counts from the PMT FPGA
        """
        self.shouldRun = False
        self.eth.clear()
  
    @inlineCallbacks
    def readNewData(self):
        if self.shouldRun:
            reading = yield self.eth.read(NUMTOCOLLECT);
            print 'packets read in: ', len(reading)    
            self.processPackets(reading)    
            reactor.callLater(0,self.readNewData)
    
    @inlineCallbacks
    def processPackets(self, packets):
        for i in range(NUMTOCOLLECT):
            message = packets[i][3]; 
            num = message[31:35]
            readout = message[36:36+16];
            if num.isdigit(): #basic version of making sure packet is formatted well
                if int(num) == 0:#if packet starts with 0000:
                    encoded = base64.b64encode(self.totalmessage)
                    if(self.count != 0):
                        yield self.dv.add([str(self.count),encoded])
                    self.count +=1
                    self.totalmessage = ''
            self.totalmessage += readout
    
if __name__ == "__main__":
    from labrad import util
    util.runServer( TimeResolvedServer() )