#Created on Aug 08, 2011
#@author: Michael Ramm, Haeffner Lab
#Thanks for code ideas from Quanta Lab, MIT
'''
### BEGIN NODE INFO
[info]
name = Pulser
version = 0.1
description = 
instancename = Pulser

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
'''

import ok
from labrad.server import LabradServer, setting
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.threads import deferToThread
import os
import numpy
import time
####

okDeviceID = 'Pulser'
devicePollingPeriod = 10

class Pulser(LabradServer):
    name = 'Pulser'
    
    def initServer(self):
        self.inCommunication = DeferredLock()
        self.connectOKBoard()
    
    def connectOKBoard(self):
        self.xem = None
        fp = ok.FrontPanel()
        module_count = fp.GetDeviceCount()
        print "Found {} unused modules".format(module_count)
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
        path = os.path.join(basepath,'lattice/okfpgaservers/pulser.bit')
        prog = xem.ConfigureFPGA(path)
        if prog: raise("Not able to program FPGA")
        pll = ok.PLL22150()
        xem.GetEepromPLL22150Configuration(pll)
        pll.SetDiv1(pll.DivSrc_VCO,4)
        xem.SetPLL22150Configuration(pll)
    
    @setting(0, "Program Sequence", sequence = '?', returns = '')
    def programSequence(self, c, sequence):
        """
        Programs Pulser with the given sequence.
        """
        if self.xem is None: raise('Board not connected')
        parsedSequence = sequence.progRepresentation()
        yield self.inCommunication.acquire()
        yield deferToThread(self._programBoard, parsedSequence)      
        self.inCommunication.release()
    
    def _programBoard(self, sequence):
        self.xem.WriteToBlockPipeIn('0xaa',1024, sequence)#address?
  
if __name__ == "__main__":
    from labrad import util
    util.runServer( Pulser() )