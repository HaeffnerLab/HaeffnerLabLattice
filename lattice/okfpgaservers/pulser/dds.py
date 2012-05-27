from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import returnValue, inlineCallbacks

class DDS(LabradServer):
    """Contains the DDS functionality for the pulser server"""
    
    newDDS = Signal() pass
    
    @setting(41, "Get DDS Channels", returns = '*s')
    def getDDSChannels(self, c):
        """get the list of available channels"""
        return self.ddsDict.keys()
    
    @setting(42, "Select DDS Channel", name = 's')
    def selectChannel(self, c, name):
        if name not in self.ddsDict.keys(): raise Exception("Incorrect DDS Channel {}".format(name))
        c['ddschan'] = name
    
    @setting(43, "Amplitude", name = 's', amplitude = 'v[dBm]', returns = 'v[dBm]')
    def amplitude(self, c, name = None, amplitude = None):
        """Get or Set the amplitude of the named channel, or of the channel selected in the current context"""
        #get the hardware channel
        if name is None:
            name = c.get('ddschan')
            if name is None: raise Exception ("Channel not provided and not selected")
        chan = self.ddsDict[name].channelnumber
        if amplitude is not None:
            #set the amplitude
            self._checkRange('amplitude', name, amplitude)
            yield self._setAmplitude(chan, amplitude)
            self.ddsDict[name] = amplitude
        #return the current amplitude
        amplitude = self.ddsDict[name]
        returnValue(amplitude)

    @setting(44, "Frequency", name = 's', frequency = 'v[MHz]', returns = 'v[MHz]')
    def frequency(self, c, name = None, frequency = None):
        """Get or Set the frequency of the named channel, or of the channel selected in the current context"""
        #get the hardware channel
        if name is None:
            name = c.get('ddschan')
            if name is None: raise Exception ("Channel not provided and not selected")
        chan = self.ddsDict[name].channelnumber
        if frequency is not None:
            #set the amplitude
            self._checkRange('frequency', name, frequency)
            yield self._setFrequency(chan, frequency)
            self.ddsDict[name] = frequency
        #return the current amplitude
        frequency = self.ddsDict[name]
        returnValue(frequency)
    
    @setting(45, 'Add DDS Pulses', channel = 's', values = '*(vv)')
    def addDDSPulse(self, c, channel, values):
        """Takes the name of the DDS channel, and the list of values in the form [(start, frequency, amplitude)]
        where frequency is in MHz, and amplitude is in dBm
        """
        hardwareAddr = self.ddsDict.get(channel).channelnumber
        sequence = c.get('sequence')
        #simple error checking
        if hardwareAddr is None: raise Exception("Unknown DDS channel {}".format(channel))
        if not sequence: raise Exception ("Please create new sequence first")
        pass
    
    def _checkRange(self, t, name, val):
        if t == 'amplitude':
            r = self.ddsDct[name].allowedamplrange
        elif t == 'frequency':
            r = self.ddsDct[name].allowedfreqrange
        if not r[0]<= val <= r[1]: raise Exception ("Value {} is outside allowed range".format(val))
    
    @inlineCallbacks
    def _setAmplitude(self, chan, ampl)
        pass
    
    @inlineCallbacks
    def _setFrequency(self, chan, freq):
        pass
            