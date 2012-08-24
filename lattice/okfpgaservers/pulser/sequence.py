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
        self.ddsSettingList = []
        self.advanceDDS = hardwareConfiguration.channelDict['AdvanceDDS'].channelnumber
        self.resetDDS = hardwareConfiguration.channelDict['ResetDDS'].channelnumber
    
    def addDDS(self, name, start, num, typ):
        timeStep = self.secToStep(start)
        self.ddsSettingList.append((name, timeStep, num, typ))
            
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
        return bool(len(self.ddsSettingList))
    
    def parseDDS(self):
        if not self.userAddedDDS(): return None
        state = self.parent._getCurrentDDS()
        pulses_end = {}.fromkeys(state, (0, 'stop')) #time / boolean whether in a middle of a pulse 
        dds_program = {}.fromkeys(state, '')
        lastTime = 0
        entries = sorted(self.ddsSettingList, key = lambda t: t[1] ) #sort by starting time
        print entries
        while True:
            try:
                name,start,num,typ = entries.pop(0)
                print name,start,num,typ
            except IndexError:
                if start  == lastTime:
                    #still have unprogrammed entries
                    self.addToProgram(dds_program, state)
                #add termination
                for name in dds_program.iterkeys():
                    dds_program[name] +=  '\x00\x00'
                #at the end of the sequence, reset dds
                lastTTL = max(self.switchingTimes.keys())
                self._addNewSwitch(lastTTL ,self.resetDDS, 1 )
                self._addNewSwitch(lastTTL + 1 ,self.resetDDS,-1)
                return dds_program
            end_time, end_typ =  pulses_end[name]
            print 'ending', end_typ
            print 'mins is ', typ
            if end_typ == typ:
                raise Exception ("Overlapping DDS Pulses Found for channel {}".format(name))
            else:
                state[name] = num
                pulses_end[name] = (start, typ)
            if start > lastTime:
                #the time has advanced, so need to program the previous state
                self.addToProgram(dds_program, state)
                if not lastTime == 0:
                    self._addNewSwitch(lastTime,self.advanceDDS,1)
                    self._addNewSwitch(lastTime + 1,self.advanceDDS,-1)
                lastTime = start

    def addToProgram(self, prog, state):
        for name,num in state.iteritems():
            if not hardwareConfiguration.ddsDict[name].remote:
                buf = self.parent._intToBuf(num)
            else:  
                buf = self.parent._intToBuf_remote(num)
            prog[name] += buf
        
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