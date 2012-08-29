from labrad.server import LabradServer, setting
from twisted.internet.defer import returnValue, inlineCallbacks
from twisted.internet.threads import deferToThread
import array
from labrad import types as T

class DDS(LabradServer):
    
    """Contains the DDS functionality for the pulser server"""
    
    @inlineCallbacks
    def initializeDDS(self):
        self.ddsLock = False
        self.api.initializeDDS()
        for channel in self.ddsDict.itervalues():
            freq,ampl = (channel.frequency, channel.amplitude)
            self._checkRange('amplitude', channel, ampl)
            self._checkRange('frequency', channel, freq)
            yield self._setParameters(channel, freq, ampl)
    
    @setting(41, "Get DDS Channels", returns = '*s')
    def getDDSChannels(self, c):
        """get the list of available channels"""
        return self.ddsDict.keys()
    
    @setting(42, "Select DDS Channel", name = 's')
    def selectChannel(self, c, name):
        if name not in self.ddsDict.keys(): raise Exception("Incorrect DDS Channel {}".format(name))
        c['ddschan'] = name
    
    @setting(43, "Amplitude", amplitude = 'v[dBm]', returns = 'v[dBm]')
    def amplitude(self, c, amplitude = None):
        """Get or Set the amplitude of the named channel, or of the channel selected in the current context"""
        #get the hardware channel
        if self.ddsLock: 
            self.ddsLock = False
            raise Exception("DDS access is locked. Running pulse sequence.")
        name = c.get('ddschan')
        if name is None: raise Exception ("Channel not provided and not selected")
        channel = self.ddsDict[name]
        if amplitude is not None:
            #set the amplitude
            amplitude = amplitude['dBm']
            self._checkRange('amplitude', channel, amplitude)
            yield self._setAmplitude(channel, amplitude)
            channel.amplitude = amplitude
        amplitude = T.Value(channel.amplitude, 'dBm')
        returnValue(amplitude)

    @setting(44, "Frequency", frequency = ['v[MHz]'], returns = ['v[MHz]'])
    def frequency(self, c, frequency = None):
        """Get or Set the frequency of the named channel, or of the channel selected in the current context"""
        #get the hardware channel
        if self.ddsLock: 
            self.ddsLock = False
            raise Exception("DDS access is locked. Running pulse sequence.")
        name = c.get('ddschan')
        if name is None: raise Exception ("Channel not provided and not selected")
        channel = self.ddsDict[name]
        if frequency is not None:
            #set the amplitude
            frequency = frequency['MHz']
            self._checkRange('frequency', channel, frequency)
            yield self._setFrequency(channel, frequency)
            channel.frequency = float(frequency)
        frequency = T.Value(channel.frequency, 'MHz')
        returnValue(frequency)
    
    @setting(45, 'Add DDS Pulses',  values = ['*(sv[s]v[s]v[MHz]v[dBm])','*(sv[s]v[s]v[MHz]v[dBm]v)'])
    def addDDSPulses(self, c, values):
        '''
        [(name, start, duration, frequency, amplitude)] where duration is duration of the pulse in seconds and high/low is a boolean
        [(name, start, duration, frequency, amplitude, phase)]
        frequency is in MHz, and amplitude is in dBm
        '''
        sequence = c.get('sequence')
        if not sequence: raise Exception ("Please create new sequence first")
        for value in values:
            try:
                name,start,dur,freq,ampl = value
                phase  = 0.0
            except ValueError:
                name,start,dur,freq,ampl,phase = value
            try:
                channel = self.ddsDict[name]
            except KeyError:
                raise Exception("Unknown DDS channel {}".format(name))
            start = start.inUnitsOf('s').value
            dur = dur.inUnitsOf('s').value
            freq = freq.inUnitsOf('MHz').value
            ampl = ampl.inUnitsOf('dBm').value
            freq_off, ampl_off = channel.off_parameters
            if freq == 0 or ampl == 0: #off state
                freq, ampl = freq_off,ampl_off
            else:
                self._checkRange('frequency', channel, freq)
                self._checkRange('amplitude', channel, ampl)
            if not channel.remote:
                num = self._valToInt(channel, freq, ampl)
                num_off = self._valToInt(channel, freq_off, ampl_off)
            else:
                num = self._valToInt_remote(channel, freq, ampl, phase)
                num_off = self._valToInt_remote(channel, freq_off, ampl_off, phase)
            #note < sign, because start can not be 0. 
            #this would overwrite the 0 position of the ram, and cause the dds to change before pulse sequence is launched
            if not self.sequenceTimeRange[0] < start <= self.sequenceTimeRange[1]: 
                raise Exception ("DDS start time out of acceptable input range for channel {0} at time {1}".format(name, start))
            if not self.sequenceTimeRange[0] < start + dur <= self.sequenceTimeRange[1]: 
                raise Exception ("DDS start time out of acceptable input range for channel {0} at time {1}".format(name, start + dur))
            if dur == 0: return #0 length pulses are ignored
            sequence.addDDS(name, start, num, 'start')
            sequence.addDDS(name, start + dur, num_off, 'stop')
        
    @setting(46, 'Get DDS Amplitude Range', returns = '(vv)')
    def getDDSAmplRange(self, c):
        name = c.get('ddschan')
        if name is None: raise Exception ("Channel not provided and not selected")
        return self.ddsDict[name].allowedamplrange
        
    @setting(47, 'Get DDS Frequency Range', returns = '(vv)')
    def getDDSFreqRange(self, c):
        name = c.get('ddschan')
        if name is None: raise Exception ("Channel not provided and not selected")
        return self.ddsDict[name].allowedfreqrange
    
    @setting(48, 'Output', state = 'b', returns =' b')
    def output(self, c, state = None):
        """To turn off and on the dds. Turning off the DDS sets the frequency and amplitude 
        to the off_parameters provided in the configuration.
        """
        if self.ddsLock: 
            self.ddsLock = False
            raise Exception("DDS access is locked. Running pulse sequence.")
        name = c.get('ddschan')
        if name is None: raise Exception ("Channel not provided and not selected")
        channel = self.ddsDict[name]
        if state is not None:
            if state and not channel.state:
                #if asked to turn on and is currently off
                yield self._setParameters(channel, channel.frequency, channel.amplitude)
            elif (channel.state and not state):
                #asked to turn off and is currently on
                freq,ampl = channel.off_parameters
                yield self._setParameters(channel, freq, ampl)
            channel.state = state
        state = channel.state
        returnValue(state)
    
    def _checkRange(self, t, channel, val):
        if t == 'amplitude':
            r = channel.allowedamplrange
        elif t == 'frequency':
            r = channel.allowedfreqrange
        if not r[0]<= val <= r[1]: raise Exception ("Value {} is outside allowed range".format(val))
    
    @inlineCallbacks
    def _setAmplitude(self, channel, ampl):
        freq = channel.frequency
        yield self.inCommunication.acquire()
        yield self._setParameters( channel, freq, ampl)
        self.inCommunication.release()
        
    @inlineCallbacks
    def _setFrequency(self, channel, freq):
        ampl = channel.amplitude
        yield self.inCommunication.acquire()
        yield self._setParameters( channel, freq, ampl)
        self.inCommunication.release()
    
    @inlineCallbacks
    def _programDDSSequence(self, dds):
        '''takes the parsed dds sequence and programs the board with it'''
        self.ddsLock = True
        for name,channel in self.ddsDict.iteritems():
            addr = channel.channelnumber
            buf = dds[name]
            if not channel.remote: 
                yield deferToThread(self._setDDSLocal, addr, buf)
            else:
                yield self._setDDSRemote(channel, addr, buf)
    
    @inlineCallbacks
    def _setParameters(self, channel, freq, ampl):
        addr = channel.channelnumber
        if not channel.remote:
            num = self._valToInt(channel, freq, ampl)
            buf = self._intToBuf(num)
            buf = buf + '\x00\x00' #adding termination
            yield deferToThread(self._setDDSLocal, addr, buf)
        else:
            num = self._valToInt_remote(channel, freq, ampl)
            buf = self._intToBuf_remote(num)
            buf = buf + '\x00\x00' #adding termination
            yield self._setDDSRemote(channel, addr, buf)
    
    def _setDDSLocal(self, addr, buf):
        self.api.resetAllDDS()
        self.api.setDDSchannel(addr)  
        self.api.programDDS(buf)
    
    @inlineCallbacks
    def _setDDSRemote(self, channel, addr, buf):
        cxn = self.remoteConnections[channel.remote]
        remote_info = self.remoteChannels[channel.remote]
        server, reset, program = remote_info.server, remote_info.reset, remote_info.program
        try:
            yield cxn.servers[server][reset]()
            yield cxn.servers[server][program]([(channel.channelnumber, buf)])
        except (KeyError,AttributeError):
            print 'Not programing remote channel {}'.format(channel.remote)
    
    def _getCurrentDDS(self):
        '''
        Returns a dictionary {name:num} with the reprsentation of the current dds state
        '''
        d = dict([(name,self._channel_to_num(channel)) for (name,channel) in self.ddsDict.iteritems()])
        return d
    
    def _channel_to_num(self, channel):
        '''returns the current state of the channel in the num represenation'''
        if channel.state:
            #if on, use current values. else, use off values
            freq,ampl = (channel.frequency, channel.amplitude)
            self._checkRange('amplitude', channel, ampl)
            self._checkRange('frequency', channel, freq)
        else:
            freq,ampl = channel.off_parameters
        if not channel.remote:
            num = self._valToInt(channel, freq, ampl)
        else:
            num = self._valToInt_remote(channel, freq, ampl)
        return num
        
    def _valToInt(self, channel, freq, ampl):
        '''
        takes the frequency and amplitude values for the specific channel and returns integer representation of the dds setting
        freq is in MHz
        power is in dbm
        '''
        ans = 0
        for val,r,m in [(freq,channel.boardfreqrange, 256**2), (ampl,channel.boardamplrange, 1)]:
            minim, maxim = r
            resolution = (maxim - minim) / float(16**4 - 1)
            seq = int((val - minim)/resolution) #sequential representation
            ans += m*seq
        return ans
    
    def _intToBuf(self, num):
        '''
        takes the integer representing the setting and returns the buffer string for dds programming
        '''
        #converts value to buffer string, i.e 128 -> \x00\x00\x00\x80
        a, b = num // 256**2, num % 256**2
        arr = array.array('B', [a % 256 ,a // 256, b % 256, b // 256])
        ans = arr.tostring()
        return ans
    
    def _valToInt_remote(self, channel, freq, ampl, phase = 0):
        '''
        takes the frequency and amplitude values for the specific channel and returns integer representation of the dds setting
        freq is in MHz
        power is in dbm
        '''
        ans = 0
        for val,r,m, precision in [(freq,channel.boardfreqrange, 1, 32), (ampl,channel.boardamplrange, 2 ** 32,  16), (phase,channel.boardphaserange, 2 ** 48,  16)]:
            minim, maxim = r
            resolution = (maxim - minim) / float(2**precision - 1)
            seq = int((val - minim)/resolution) #sequential representation
            ans += m*seq
        return ans
    
    def _intToBuf_remote(self, num):
        '''
        takes the integer representing the setting and returns the buffer string for dds programming
        '''
        freq_num = num % 2**32
        a, b = freq_num // 256**2, freq_num % 256**2
        freq_arr = array.array('B', [b % 256 ,b // 256, a % 256, a // 256])
        
        phase_ampl_num = num // 2**32
        a, b = phase_ampl_num // 256**2, phase_ampl_num % 256**2
        phase_ampl_arr = array.array('B', [a % 256 ,a // 256, b % 256, b // 256])
        
        ans = phase_ampl_arr.tostring() + freq_arr.tostring()
        return ans