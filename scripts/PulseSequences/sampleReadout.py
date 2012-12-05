from PulseSequence import PulseSequence
from labrad.units import WithUnit

class sampleReadout(PulseSequence):

    def sequence(self):
        start =  WithUnit(100, 'us')
        duration = WithUnit(10, 'ms')
        self.ttl_pulses.append(('ReadoutCount', start, duration))
        self.ttl_pulses.append(('TimeResolvedCount',start, duration))
        
        
if __name__ == '__main__':
    
    import labrad
    import numpy as np
    cxn = labrad.connect()
    pulser = cxn.pulser
    cs = sampleReadout(**{})
    cs.programSequence(cxn.pulser)
    
    cxn.pulser.start_number(1000)
    cxn.pulser.wait_sequence_done()
    cxn.pulser.stop_sequence()
    readout = cxn.pulser.get_readout_counts().asarray
#    timetags = pulser.get_timetags().asarray
    print np.average(readout)
#    print timetags
#    print timetags.size