'''
Created on Sept 6, 2011
@author: Michael Ramm, Haeffner Lab
'''
import ok
from labrad.server import LabradServer, setting
from twisted.internet import reactor
from twisted.internet.defer import DeferredLock, returnValue, inlineCallbacks
from twisted.internet.threads import deferToThread
from labrad import util
import os
import time

okDeviceID = 'Trigger'
devicePollingPeriod = 10
timeout = 1

class TriggerFPGA(LabradServer):
    name = 'Trigger'
    
    def initServer(self):
        self.inCommunication = DeferredLock()
        self.connectOKBoard()
        self.dict = {
                     'Triggers':{'PaulBox':0},
                     'Switches':{'866':(0x01,True), 'BluePI':(0x02,True)}
                     }
    
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
        path = os.path.join(basepath,'lattice/okfpgaservers/trigger.bit')
        prog = xem.ConfigureFPGA(path)
        if prog: raise("Not able to program FPGA")
        pll = ok.PLL22150()
        xem.GetEepromPLL22150Configuration(pll)
        pll.SetDiv1(pll.DivSrc_VCO,4)
        xem.SetPLL22150Configuration(pll)
    
    def _isSequenceDone(self):
        self.xem.UpdateTriggerOuts()
        return self.xem.IsTriggered()
    
    def _trigger(self, channel):
        self.xem.ActivateTriggerIn(0x40, channel)
    
    def _switch(self, channel, value):
        if value:
            self.xem.SetWireInValue(0x00,channel,channel)
        else:
            self.xem.SetWireInValue(0x00,0x00,channel)
    
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
        if channelName not in self.dict['Triggers']: raise Exception("Incorrect Channel")
        yield self.inCommunication.acquire()
        channel = self.dict['Triggers'][channelName]
        yield deferToThread(self._trigger, channel)
        yield self.inCommunication.release()
    
    @setting(3, 'Switch', channelName = 's', state= 'b')
    def switch(self, c, channelName):  
        """
        Swtiches the given channel
        """
        if channelName not in self.dict['Switches']: raise Exception("Incorrect Channel")
        if not self.dict['Switches'][channelName][1]: state = not state #allows for easy reversal of high/low
        yield self.inCommunication.acquire()
        channel = self.dict['Switches'][channelName]
        yield deferToThread(self._switch, channel, state)
        yield self.inCommunication.release()
        
    @setting(4, 'Wait for PBox Completion', timeout = 'v', returns = 'b')
    def setCollectTime(self, c, timeout = 10):
        """
        Returns true if Paul Box sequence has completed within a timeout period
        """
        time = float(time)
        if not 0.0<time<5.0: raise('incorrect collection time')
        if mode not in self.collectionTime.keys(): raise("Incorrect mode")
        if mode == 'Normal':
            self.collectionTime[mode] = time
            yield self.inCommunication.acquire()
            self._setUpdateTime(time)
            self.inCommunication.release()
        elif mode == 'Differential':
            self.collectionTime[mode] = time

if __name__ == "__main__":
    from labrad import util
    util.runServer( TriggerFPGA() )