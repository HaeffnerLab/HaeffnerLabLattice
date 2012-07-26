'''
### BEGIN NODE INFO
[info]
name = Pulser_729
version = 0.2
description =
instancename = Pulser_729

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
'''
from labrad.server import LabradServer, setting
from twisted.internet.defer import DeferredLock, inlineCallbacks
from twisted.internet.threads import deferToThread
from api import api

class Pulser_729(LabradServer):
    
    name = 'pulser_729'
    
    @inlineCallbacks    
    def initServer(self):
        self.api  = api()
        self.inCommunication = DeferredLock()
        yield self.initializeBoard()
    
    @inlineCallbacks
    def initializeBoard(self):
        connected = self.api.connectOKBoard()
        while not connected:
            print 'not connected, waiting for 10 seconds to try again'
            yield self.wait(10.0)
            connected = self.api.connectOKBoard()
    
    @setting(0, 'Reset DDS', returns = '')
    def resetDDS(self , c):
        """
        Reset the DDS position
        """
        yield self.inCommunication.acquire()
        yield deferToThread(self.api.resetAllDDS)
        self.inCommunication.release()
        
    @setting(1, "Program DDS", returns = '*(is)')
    def programDDS(self, c, program):
        """
        Programs the DDS, the input is a tuple of channel numbers and buf objects for the channels
        """
        yield self.inCommunication.acquire()
        yield deferToThread(self._programDDSSequence, program)
        self.inCommunication.release()
    
    def _programDDSSequence(self, program):
        '''takes the parsed dds sequence and programs the board with it'''
        for chan, buf in program:
            self.api.setDDSchannel(chan)
            self.api.programDDS(buf)
        self.api.resetAllDDS()
        
#    def _valToInt(self, chan, freq, ampl, phase = 0):
#        '''
#        takes the frequency and amplitude values for the specific channel and returns integer representation of the dds setting
#        freq is in MHz
#        power is in dbm
#        '''
#        config = self.ddsDict[chan]
#        ans = 0
#        for val,r,m, precision in [(freq,config.boardfreqrange, 1, 32), (ampl,config.boardamplrange, 2 ** 32,  16), (phase,config.boardphaserange, 2 ** 48,  16)]:
#            minim, maxim = r
#            resolution = (maxim - minim) / float(2**precision - 1)
#            seq = int((val - minim)/resolution) #sequential representation
#            ans += m*seq
#        return ans
#    
#    def _intToBuf(self, num):
#        '''
#        takes the integer representing the setting and returns the buffer string for dds programming
#        '''
#        freq_num = num % 2**32
#        a, b = freq_num // 256**2, freq_num % 256**2
#        freq_arr = array.array('B', [b % 256 ,b // 256, a % 256, a // 256])
#        
#        phase_ampl_num = num // 2**32
#        a, b = phase_ampl_num // 256**2, phase_ampl_num % 256**2
#        phase_ampl_arr = array.array('B', [a % 256 ,a // 256, b % 256, b // 256])
#        
#        ans = phase_ampl_arr.tostring() + freq_arr.tostring()
#        return ans
if __name__ == "__main__":
    from labrad import util
    util.runServer( Pulser_729() )