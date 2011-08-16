'''
Created on Feb 11, 2011

@author: Michael Ramm, christopherreilly
'''
from labrad.server import LabradServer, setting
from twisted.internet import reactor
from twisted.internet.defer import returnValue, inlineCallbacks
import base64

ADAPTER = 1
DEFAULT_SAVE_FOLDER = ['','TimeResolvedCounts'] #where to save data, unless specified
TIMEOUT = 1 #day how long to wait for data
NUMTOCOLLECT = 1000 #number of packets to read in at one time
SOURCEMAC = '00:AA:BB:CC:DD:EE'

#handling of ethernet server not found (wait for it to connect)
#exception if serial port times out

class TimeResolvedServer(LabradServer):
    
    name = 'Time Resolved Server'
    
    @inlineCallbacks
    def initServer(self):
        try:
            #establish connection with ethernet server
            self.eth = self.client.lattice_pc_direct_ethernet
            self.eth.connect(ADAPTER)
            self.eth.require_source_mac(SOURCEMAC)
            self.eth.timeout(TIMEOUT)#sets timeout to 1 DAY, how long collect function waits before it returns error
        except:
            print 'ethernet server not found'
            raise
        try:
            self.dv = self.client.data_vault
            self.dv.cd(DEFAULT_SAVE_FOLDER,True)
            dataset = yield self.dv.new('TimeResolvedcounts',['Trial'],['Counts'],'s')
        except:
            print 'data vault not found'
            raise
        self.createDict(dataset[1])
        self.shouldRun = False
               
    def createDict(self, dataset):
        self.d = {
                  'DataSet':dataset,
                  'TrialCount':0,
                  'TotalMessage':''
                  }
            
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
        
    @setting(2, returns = 'b')
    def isReceiving(self,c):
        return self.shouldRun
    
    @setting(3, returns = 's')
    def currentDataSet(self,c):
        return self.d['DataSet']
    
    @setting(4, returns = 's')
    def newDataSet(self,c):
        dataset = yield self.dv.new('TimeResolvedcounts',['Trial'],['Counts'],'s')
        self.d['DataSet'] = dataset[1]
        self.d['TrialCount'] = 0
        self.d['TotalMessage'] = ''
        returnValue(self.d['DataSet'])
  
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
                if int(num) == 0:#if packet starts with 0000, then add the message unless it's the first one
                    encoded = base64.b64encode(self.d['TotalMessage'])
                    if self.d['TrialCount'] is not 0:
                        yield self.dv.add([str(self.d['TrialCount']),encoded])
                        ###testing to see how many counts we have for a low count rate
                        #ct1 = (encoded.count('B') + encoded.count('C') + encoded.count('E') + encoded.count('I') + encoded.count('Q') + encoded.count('g'))
                        #ct2 = 2 * (len(encoded) - encoded.count('A') - ct1)
                        #print ct1 + ct2
                    self.d['TrialCount'] += 1
                    self.d['TotalMessage'] = ''
            self.d['TotalMessage'] += readout
            
if __name__ == "__main__":
    from labrad import util
    util.runServer( TimeResolvedServer() )