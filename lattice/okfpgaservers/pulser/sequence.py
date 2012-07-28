import numpy
from hardwareConfiguration import hardwareConfiguration

class Sequence():
    """Sequence for programming pulses"""
    def __init__(self, parent):
        self.parent = parent
        self.channelTotal = hardwareConfiguration.channelTotal
        self.timeResolution = hardwareConfiguration.timeResolution
        self.MAX_SWITCHES = hardwareConfiguration.maxSwitches
        #dictionary in the form time:which channels to switch
        #time is expressed as timestep with the given resolution
        #which channels to switch is a channelTotal-long array with 1 to switch ON, -1 to switch OFF, 0 to do nothing
        self.switchingTimes = {0:numpy.zeros(self.channelTotal, dtype = numpy.int8)} 
        self.switches = 1 #keeps track of how many switches are to be performed (same as the number of keys in the switching Times dictionary"
        #dictionary for storing information about dds switches, in the format:
        #timestep: {channel_name: integer representing the state}
        self.ddsSettings = {}
        self.advanceDDS = hardwareConfiguration.channelDict['AdvanceDDS'].channelnumber
        self.resetDDS = hardwareConfiguration.channelDict['ResetDDS'].channelnumber
        
    def addDDS(self, name, start, setting):
        '''add DDS setting'''
        timeStep = self.secToStep(start)
        if self.ddsSettings.has_key(timeStep):
            #check for duplicate entry
            if self.ddsSettings[timeStep].has_key(name): raise Exception ('Double setting at time {} for DDS channel {}'.format(timeStep, name))
        else:
            #else, create it
            self.ddsSettings[timeStep] = {}
        self.ddsSettings[timeStep][name] = setting
            
    def addPulse(self, channel, start, duration):
        """adding TTL pulse, times are in seconds"""
        start = self.secToStep(start)
        duration = self.secToStep(duration)
        self._addNewSwitch(start, channel, 1)
        self._addNewSwitch(start + duration, channel, -1)
    
    def extendSequenceLength(self, timeLength):
        """Allows to extend the total length of the sequence"""
        timeLength = self.secToStep(timeLength)
        self._addNewSwitch(timeLength,0,0)

    def secToStep(self, sec):
        '''converts seconds to time steps'''
        return int( sec / self.timeResolution) 
    
    def numToHex(self, number):
        '''converts the number to the hex representation for a total of 32 bits
        i.e: 3 -> 00000000...000100 ->  \x00\x00\x03\x00, note that the order of 8bit pieces is switched'''
        a,b = number // 65536, number % 65536
        return str(numpy.uint16([a,b]).data)

    def _addNewSwitch(self, timeStep, chan, value):
        if self.switchingTimes.has_key(timeStep):
            if self.switchingTimes[timeStep][chan]: raise Exception ('Double switch at time {} for channel {}'.format(timeStep, chan))
            self.switchingTimes[timeStep][chan] = value
        else:
            if self.switches == self.MAX_SWITCHES: raise Exception("Exceeded maximum number of switches {}".format(self.switches))
            self.switchingTimes[timeStep] = numpy.zeros(self.channelTotal, dtype = numpy.int8)
            self.switches += 1
            self.switchingTimes[timeStep][chan] = value
    
    def progRepresentation(self):
        ddsSettings = self.parseDDS()
        ttlProgram = self.parseTTL()
        return ddsSettings, ttlProgram
    
    def userAddedDDS(self):
        return bool(len(self.ddsSettings.keys()))
    
    def parseDDS(self):
        '''uses the ddsSettings dictionary to create an easily programmable list in the form
        {channel_name : buf}
        The length of each bufstring is equal because all the ttl settings are advanced together:
        If a setting doesn't change, it's repeated.
        During the parsing the necessary ttls to advance dds settings are added automatically.
        At the end of the pulse sequence, the ram position of dds is set again to the initial value of 0.
        '''
        if not self.userAddedDDS(): return None
        dds_program = {}
        state = {}
        for timeStep,new_setting in sorted(self.ddsSettings.iteritems()):
            state.update(new_setting)
            for name,num in state.iteritems():
                if not hardwareConfiguration.ddsDict[name].remote:
                    buf = self.parent._intToBuf(num)
                else:  
                    buf = self.parent._intToBuf_remote(num)
                try:
                    dds_program[name] += buf
                except KeyError: #first addition
                    dds_program[name] = buf
            #advance the state of the dds by settings the advance channel high for one timestep
            #print self.ddsSettings
            print timeStep
            if not timeStep == 0:
                self._addNewSwitch(timeStep,self.advanceDDS,1)
                self._addNewSwitch(timeStep + 1,self.advanceDDS,-1)
        #at the end of the sequence, reset dds
        lastTTL = max(self.switchingTimes.keys())
        self._addNewSwitch(lastTTL ,self.resetDDS, 1 )
        self._addNewSwitch(lastTTL + 1 ,self.resetDDS,-1)
        #add termination
        for name in dds_program.iterkeys():
            dds_program[name] +=  '\x00\x00'
        return dds_program
        
    def parseTTL(self):
        """Returns the representation of the sequence for programming the FPGA"""
        rep = ''
        lastChannels = numpy.zeros(self.channelTotal)
        powerArray = 2**numpy.arange(self.channelTotal, dtype = numpy.uint64)
        for key,newChannels in sorted(self.switchingTimes.iteritems()):
            channels = lastChannels + newChannels #computes the action of switching on the state
            if (channels < 0).any(): raise Exception ('Trying to switch off channel that is not already on')
            channelInt = numpy.dot(channels,powerArray)
            rep = rep + self.numToHex(key) + self.numToHex(channelInt) #converts the new state to hex and adds it to the sequence
            lastChannels = channels
        rep = rep + 2*self.numToHex(0) #adding termination
        return rep
    
    def humanRepresentation(self):
        """Returns the human readable version of the sequence for FPGA for debugging"""
        dds,rep = self.progRepresentation()
        arr = numpy.fromstring(rep, dtype = numpy.uint16) #does the decoding from the string
        arr = numpy.array(arr, dtype = numpy.uint32) #once decoded, need to be able to manipulate large numbers
        arr = arr.reshape(-1,4)
        times =( 65536  *  arr[:,0] + arr[:,1]) * self.timeResolution
        channels = ( 65536  *  arr[:,2] + arr[:,3])

        def expandChannel(ch):
            '''function for getting the binary representation, i.e 2**32 is 1000...0'''
            expand = bin(ch)[2:].zfill(32)
            reverse = expand[::-1]
            return reverse
        
        channels = map(expandChannel,channels)
        return numpy.vstack((times,channels)).transpose()