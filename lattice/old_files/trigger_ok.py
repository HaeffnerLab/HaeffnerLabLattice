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
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import DeferredLock, returnValue
from twisted.internet.threads import deferToThread
import os
import time

okDeviceID = 'Trigger'
devicePollingPeriod = 10

SIGNALID = 611051

class TriggerFPGA(LabradServer):
    name = 'Trigger'
    onNewUpdate = Signal(SIGNALID, 'signal: switch toggled', '(ss)')
    
    def initServer(self):
        self.inCommunication = DeferredLock()
        self.connectOKBoard()
        #create dictionary for triggers and switches in the form 'trigger':channel;'switch:{}
        #the state written below represents the initial state of the server
        self.dict = {
                     'Triggers':{'PaulBox':0},
                     'Switches':{
                                 'bluePI':
                                     {'chan':       0x01,
                                      'ismanual':   True,
                                      'manstate':   False,
                                      'maninv':     False,
                                      'autoinv':    False
                                      },
                                 'crystallization':
                                     {'chan':       0x02,
                                      'ismanual':   True,
                                      'manstate':   True,
                                      'maninv':     True,
                                      'autoinv':    False
                                      },
                                '866DP':
                                     {'chan':       0x04,
                                      'ismanual':   False,
                                      'manstate':   True,
                                      'maninv':     False,
                                      'autoinv':    True,
                                      },
#                                '110DP':
#                                     {'chan':       0x08,
#                                      'ismanual':   True,
#                                      'manstate':   True,
#                                      'maninv':     False,
#                                      'autoinv':    False
#                                      },
#                                '220SP':
#                                     {'chan':       0x10,
#                                      'ismanual':   True,
#                                      'manstate':   True,
#                                      'maninv':     False,
#                                      'autoinv':    False
#                                      },
                                '110DP':
                                     {'chan':       0x20,
                                      'ismanual':   True,
                                      'manstate':   True,
                                      'maninv':     False,
                                      'autoinv':    False
                                      },
                                'axial':
                                     {'chan':       0x40,
                                      'ismanual':   True,
                                      'manstate':   True,
                                      'maninv':     False,
                                      'autoinv':    False
                                      }
                                 }
                     }        
        self.updateSwitches()
        self.listeners = set()
        
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
    
    def updateSwitches(self):
        """updates the switches to the current dictionary values"""
        ep00 = 0 #programming arrays, see page70 Hong notebook
        ep01 = 0
        for switchName in self.dict['Switches'].keys():
            channel = self.dict['Switches'][switchName]['chan']
            ismanual = self.dict['Switches'][switchName]['ismanual']
            manstate = self.dict['Switches'][switchName]['manstate']
            maninv = self.dict['Switches'][switchName]['maninv']
            autoinv = self.dict['Switches'][switchName]['autoinv']
            ep00 = ep00 + channel * ismanual
            if ismanual:
                if maninv: manstate = not manstate
                ep01 = ep01 + channel * manstate
            else:
                ep01 = ep01 + channel * autoinv
        self._switch( ep00, ep01)
        
    def _isSequenceDone(self):
        self.xem.UpdateTriggerOuts()
        return self.xem.IsTriggered(0x6A,0b00000001)
    
    def _trigger(self, channel):
        self.xem.ActivateTriggerIn(0x40, channel)
    
    def _switch(self, ep00, ep01):
        self.xem.SetWireInValue(0x00,ep00,0xFF)
        self.xem.SetWireInValue(0x01,ep01,0xFF)
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
    
    @setting(3, 'Switch Manual', channelName = 's', state= 'b', invert = 'b')
    def switchManual(self, c, channelName, state = None, invert = None):  
        """
        Switches the given channel into the manual mode, by default will go into the last remembered state but can also
        pass the argument which state it should go into, and whether commands should be inverted.
        """
        if channelName not in self.dict['Switches'].keys(): raise Exception("Incorrect Channel")
        self.dict['Switches'][channelName]['ismanual'] = True
        if state is not None:
            self.dict['Switches'][channelName]['manstate'] = state
        if invert is not None:
            self.dict['Switches'][channelName]['maninv'] = invert
        yield self.inCommunication.acquire()
        yield deferToThread(self.updateSwitches)
        yield self.inCommunication.release()
        newstate = self.dict['Switches'][channelName]['manstate']
        if newstate:
            self.notifyOtherListeners(c,(channelName,'ManualOn'))
        else:
            self.notifyOtherListeners(c,(channelName,'ManualOff'))

    @setting(4, 'Switch Auto', channelName = 's', invert= 'b')
    def switchAuto(self, c, channelName, invert = None):  
        """
        Switches the given channel into the automatic mode, with an optional inversion.
        """
        if channelName not in self.dict['Switches'].keys(): raise Exception("Incorrect Channel")
        self.dict['Switches'][channelName]['ismanual'] = False
        if invert is not None:
            self.dict['Switches'][channelName]['autoinv'] = invert
        yield self.inCommunication.acquire()
        yield deferToThread(self.updateSwitches)
        yield self.inCommunication.release()
        self.notifyOtherListeners(c,(channelName,'Auto'))
            
    @setting(5, 'Get State', channelName = 's', returns = '(bbbb)')
    def getState(self, c, channelName):
        """
        Returns the current state of the switch: in the form (Manual/Auto, ManualOn/Off, ManualInversionOn/Off, AutoInversionOn/Off)
        """
        if channelName not in self.dict['Switches'].keys(): raise Exception("Incorrect Channel")
        ismanual = self.dict['Switches'][channelName]['ismanual']
        manstate = self.dict['Switches'][channelName]['manstate']
        maninv = self.dict['Switches'][channelName]['maninv']
        autoinv = self.dict['Switches'][channelName]['autoinv']
        answer = (ismanual,manstate,maninv,autoinv)
        return answer
        
    @setting(6, 'Wait for PBox Completion', timeout = 'v', returns = 'b')
    def waitForPBDone(self, c, timeout = 10):
        """
        Returns true if Paul's Box sequence has completed within a timeout period
        """
        requestCalls = int(timeout / 0.050 ) #number of request calls
        print requestCalls
        for i in range(requestCalls):
            yield self.inCommunication.acquire()
            done = yield deferToThread(self._isSequenceDone)
            yield self.inCommunication.release()
            if done: returnValue(True)
            yield deferToThread(time.sleep, 0.050)
        returnValue(False)
        
    def notifyOtherListeners(self, context, message):
        """
        Notifies all listeners except the one in the given context
        """
        notified = self.listeners.copy()
        notified.remove(context.ID)
        self.onNewUpdate(message, notified)     
            
    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)
                           

if __name__ == "__main__":
    from labrad import util
    util.runServer( TriggerFPGA() )