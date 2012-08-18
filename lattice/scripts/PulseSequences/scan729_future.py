from subsequences.DopplerCooling import DopplerCooling
from subsequences.EmptySequence import EmptySequence
from SemaphoreSequence import SemaphoreSequence
from labrad import types as T

class CompositeSequence(SemaphoreSequence):
    
    def coniguration(self):
        return {}
    
    def sequence(self):
        print self.start, self.end
        self.addSequence(DopplerCooling)
        print self.start, self.end
        self.addSequence(EmptySequence, **{'duration': T.Value(10.0, 'us')})
        print self.start, self.end
        self.addSequence(DopplerCooling, position = 10)
        print self.start, self.end
        print self.dds_pulses

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    replace = {'doppler_cooling_duration':T.Value(1.0,'ms')}
    cs = CompositeSequence(cxn.semaphore, **replace)