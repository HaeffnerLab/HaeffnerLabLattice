'''
Created on Apr 7, 2011
Modified July 26, 2011
@author: Michael Ramm
'''
from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from twisted.internet.defer import returnValue
from twisted.internet.threads import deferToThread
from labrad.types import Error
import time
import subprocess as sp
from twisted.internet import reactor

NUMCHANNELS = 16
TIMEOUT = 1.0
BAUDRATE = 115200
DelayWhenSwtch = 300 #additional delay needed to complete switching
SetExposureFile = 'setExposure.exe'
GetFreqFile = 'getFreq.exe'


class Multiplexer( SerialDeviceServer ):
    '''
    LabRAD Sever for interfacing with the Wavemeter and the Multiplexer
    '''  
    class channelInfo():
        
        class channel():
            def __init__(self, chanName, chanNumber, wavelength, state, exposureTime):
                self.chanName = chanName
                self.chanNumber = chanNumber #what's written on the box i.e 1,2,3 and is used by the serial port
                self.wavelength = wavelegth
                self.state = state
                self.exp = exposureTime
                self.freq = None

    name = 'Multiplexer Server' 
    regKey = 'Multiplexer'
    port = None
    serNode = 'lab-49'
    timeout = TIMEOUT


    @inlineCallbacks
    def initServer( self ):
        self.createChannelInfo()
        ####self.channelinfolist = yield self.loadChanInfo()
        ####self.wllist = self.loadwlList()
        print [(i.state,i.exp) for i in self.channelinfolist]
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
        port = yield self.getPortFromReg( self.regKey )
        self.port = port
        try:
            serStr = yield self.findSerial( self.serNode )
            self.initSerial( serStr, port, baudrate = BAUDRATE )
        except SerialConnectionError, e:
            self.ser = None
            if e.code == 0:
                print 'Could not find serial server for node: %s' % self.serNode
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
            else: raise
        self.isCycling = False
    
    def createDict(self):
        self.d = {}
        self.d['397'] = ChannelInfo(chanName = '397', chanNumer = )
        
    ####def loadwlList(self):
        d = [None for ch in range(NUMCHANNELS)]
        d[3] = '422'
        d[4]=  '397'
        d[5] = '866'
        d[9] = '732'
        return d
    
    @inlineCallbacks
    def loadChanInfo(self):
        reg = self.client.registry
        yield reg.cd(['','Servers','Multiplexer'],True)
        try:
            regInfo = yield reg.get('channelinfo')
            channelinfo = [self.ChannelInfo(i[0],i[1]) for i in regInfo]
        except Error, e:
            if e.code is 21:
                channelinfo = [self.ChannelInfo(1,1) for i in range(NUMCHANNELS)]
        returnValue(channelinfo)
    
    @inlineCallbacks
    def saveChannelInfo(self):
        info = [(channel.state,channel.exp) for channel in self.channelinfolist]
        yield self.client.registry.set('channelinfo',info)
    
    def validateInput(self, input, type):
        if type is 'channel':
            if input not in range(NUMCHANNELS):
                raise Error('channel out of range')
        if type is 'connectedchannel':
            connectedCh = [index for index,wl in enumerate(self.wllist) if wl is not None]
            if input not in connectedCh:
                raise Error('this channel not connected')
        if type is 'exposure':
            if not 0 <= input <= 2000:
                raise Error('exposure invalid')   
        if type is 'wavelength':
            if not input in self.wllist:
                raise Error('No channel corresponding to selected frequency')    
    
    @inlineCallbacks
    def _setExposure(self, exp):
        yield deferToThread(sp.Popen(SetExposureFile, shell=False, stdin = sp.PIPE).communicate, str(exp))
    
    @inlineCallbacks
    def _getFreq(self):
        result = yield deferToThread(sp.Popen(GetFreqFile, shell=False, stdout = sp.PIPE).communicate)
        returnValue(result[0])
    
    @inlineCallbacks
    def _switchChannel(self, chan):
        line = 'I1 ' + str(chan+ 1) +'\r' #format specified by DiCon Manual p7
        yield self.ser.write(line)
    
    @setting(0,'Start Cycling', returns = '')
    def startCycling(self,c):
        self.isCycling = True
        self.measureChan()
        
    @inlineCallbacks
    def measureChan(self, prevChannel = None ):
        if not self.isCycling: return
        activeChannels = [index for index, state in enumerate([channel.state for channel in self.channelinfolist]) if state]
        if not activeChannels:
            reactor.callLater(.5, self.measureChan)
            return
        if prevChannel is None or prevChannel not in activeChannels:
            channel = activeChannels[0]
            prevChannel = channel
            isSwitching = True
        else:
            channel = activeChannels[(activeChannels.index(prevChannel) + 1) % len(activeChannels)]
            isSwitching = channel is not prevChannel
        prevExp, curExp = [self.channelinfolist[channel].exp for channel in (prevChannel, channel)]
        if isSwitching:
            print 'switching channel to ', channel
            yield self._switchChannel(channel)
        yield self._setExposure(curExp)
        print 'setting current exposure to ', curExp 
        if isSwitching:
            waittime = prevExp + curExp + DelayWhenSwtch
            yield deferToThread(time.sleep, waittime / 1000.0)
        else:
            yield deferToThread(time.sleep, .1)
        freq = yield self._getFreq()
        print 'found freq of', freq, 'for channel', channel
        self.channelinfolist[channel].freq = freq
        reactor.callLater(0,self.measureChan, channel)
                
    @setting(1,'Stop Cycling', returns = '')
    def stopCycling(self,c):
        self.isCycling = False
    
    @setting(2,'Get Frequency',channel = 'w: which channel',returns ='v: laser frequency') ####
    def getFreq(self,c, channel):
        return self.channelinfolist[channel].freq
    
    @setting(3,'Get Frequencies', returns ='*v: laser frequencies') ####
    def getFreqs(self,c):
        return [chan.freq for chan in self.channelinfolist]

    @setting(4,'Get Selected Channels', returns='*w: which channels are selected') ####
    def getActiveChans(self,c):
        return [ index for index, state in enumerate( [channel.state for channel in self.channelinfolist]) if state ]
    
    @setting(5,'Get Exposures',returns='*w: exposure times for all channels') ####
    def getExposures(self,c):
        return [ chan.exp for chan in self.channelinfolist ]
    
    @setting(6,'Toggle Channel', channel = 'w', state='b', returns='') ####
    def toggleChan(self,c,channel, state):
        self.validateInput(channel,'channel')
        self.channelinfolist[channel].state = int(state)
        yield self.saveChannelInfo()
    
    @setting(7,'Set Exposure', channel = 'w', exposure='w',returns='') ####
    def setExposure(self,c,channel,exposure):
        self.validateInput(channel,'channel')
        self.validateInput(exposure,'exposure')
        self.channelinfolist[channel].exp = exposure
        self.saveChannelInfo()
    
    @setting(8,'Select One Channel', selectedch = 'w', returns = '') ####
    def selectOneChan(self,c,selectedch):
        for ch in range(NUMCHANNELS):
            if selectedch == ch:
                self.channelinfolist[ch].state = 1
            else:
                self.channelinfolist[ch].state = 0
    
    @setting(9, 'Get Wavelength From Channel', channel = 'w', returns = 's') ####
    def wlfromch(self, c, channel):
        self.validateInput(channel,'connectedchannel')
        return self.wllist[channel]
    
    @setting(10, 'Get Channel From Wavelength', wl = 's', returns = 'w') ####
    def chfromwl(self, c, wl):
        self.validateInput(wl,'wavelength')
        return self.wllist.index(wl)
    
    @setting(11, 'Is Cycling',returns = 'b')
    def isCycling(self,c):
        return self.isCycling
        
if __name__ == "__main__":
    from labrad import util
    util.runServer(Multiplexer())    

