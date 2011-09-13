#Created on Sept 6, 2011
#@author: Michael Ramm, Haeffner Lab

"""
### BEGIN NODE INFO
[info]
name = Trigger
version = 1.0
description = 
instancename = Trigger

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import ok
from labrad.server import LabradServer, setting
from twisted.internet import reactor
from twisted.internet.defer import DeferredLock, returnValue
from twisted.internet.threads import deferToThread
import os
import time

okDeviceID = 'Trigger'
devicePollingPeriod = 10

class TriggerFPGA(LabradServer):
    name = 'Trigger'
    
    def initServer(self):
        self.inCommunication = DeferredLock()
        self.connectOKBoard()
        #create dictionary for triggers and switches in the form 'trigger':channel;'switch:(channel , logicnotnegated, isTrueAtStart'
        self.dict = {
                     'Triggers':{'PaulBox':0},
                     'Switches':{'866':(0x01,True, True), 'BluePI':(0x02,True, False), '397LocalHeating':(0x04,True,False)}
                     }
        self.initializeChannels()
        
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
        path = os.path.join(basepath,'lattice/okfpgaservers/trigger.bit')
        prog = xem.ConfigureFPGA(path)
        if prog: raise("Not able to program FPGA")
        pll = ok.PLL22150()
        xem.GetEepromPLL22150Configuration(pll)
        pll.SetDiv1(pll.DivSrc_VCO,4)
        xem.SetPLL22150Configuration(pll)
    
    def initializeChannels(self):
        for switchName in self.dict['Switches'].keys():
            channel = self.dict['Switches'][switchName][0]
            value = self.dict['Switches'][switchName][1]
            initialize = self.dict['Switches'][switchName][2]
            if initialize:
                print 'initializing {0} to {1}'.format(switchName, value)
                self._switch( channel, value)
        
    def _isSequenceDone(self):
        self.xem.UpdateTriggerOuts()
        return self.xem.IsTriggered(0x6A,0b00000001)
    
    def _trigger(self, channel):
        self.xem.ActivateTriggerIn(0x40, channel)
    
    def _switch(self, channel, value):
        if value:
            self.xem.SetWireInValue(0x00,channel,channel)
        else:
            self.xem.SetWireInValue(0x00,0x00,channel)
        self.xem.UpdateWireIns()
    
    @setting(0, 'Get Trigger Channels', returns = '*s')
    def getTriggerChannels(self, c):
        """
        Returns available channels for triggering
        """
        return self.dict['Triggers'].keys()
    
    @setting(1, 'Get Switching Channels', returns = '*s')
    def getSwitchingChannels(self, c):
        """
        Returns available channels for switching
        """
        return self.dict['Switches'].keys()
    
    @setting(2, 'Trigger', channelName = 's')
    def trigger(self, c, channelName):
        """
        Triggers the select channel
        """
        if channelName not in self.dict['Triggers'].keys(): raise Exception("Incorrect Channel")
        yield self.inCommunication.acquire()
        channel = self.dict['Triggers'][channelName]
        yield deferToThread(self._trigger, channel)
        yield self.inCommunication.release()
    
    @setting(3, 'Switch', channelName = 's', state= 'b')
    def switch(self, c, channelName, state):  
        """
        Switches the given channel
        """
        if channelName not in self.dict['Switches'].keys(): raise Exception("Incorrect Channel")
        if not self.dict['Switches'][channelName][1]: state = not state #allows for easy reversal of high/low
        yield self.inCommunication.acquire()
        channel = self.dict['Switches'][channelName][0]
        yield deferToThread(self._switch, channel, state)
        yield self.inCommunication.release()
        
    @setting(4, 'Wait for PBox Completion', timeout = 'v', returns = 'b')
    def setCollectTime(self, c, timeout = 10):
        """
        Returns true if Paul Box sequence has completed within a timeout period
        """
        requestCalls = int(timeout / 0.050 ) #number of request calls
        for i in range(requestCalls):
            yield self.inCommunication.acquire()
            done = yield deferToThread(self._isSequenceDone)
            yield self.inCommunication.release()
            if done: returnValue(True)
            yield deferToThread(time.sleep, 0.050)
        returnValue(False)
            
            
            
                           

if __name__ == "__main__":
    from labrad import util
    util.runServer( TriggerFPGA() )