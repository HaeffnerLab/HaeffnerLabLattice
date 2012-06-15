from sequence import Sequence
from plotsequence import SequencePlotter
import time
import numpy

class sampleDDS(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                    }
    

    def defineSequence(self):
        pulser = self.pulser
        p = self.parameters
        pwrs = numpy.linspace(-13,-3,101)
        print pwrs
        for iter,p in enumerate(pwrs):
            t = 100e-9 + iter * .05
            f = 219.6 + iter * .04
            pulser.add_dds_pulses('axial', [(t , 220.0 , p)])
        
        
if __name__ == '__main__':
    for i in range(50):
        import labrad
        cxn = labrad.connect()
        pulser = cxn.pulser
        seq = sampleDDS(pulser)
        pulser.new_sequence()
        seq.defineSequence()
        pulser.program_sequence()
        pulser.start_single()
    #    pulser.start_number(100)
        #time.sleep(2)
        pulser.wait_sequence_done(1000.0)
        #print 'completed', pulser.repeatitions_completed()
        pulser.stop_sequence()
        #print 'completed', pulser.repeatitions_completed()
    #    hr = pulser.human_readable().asarray
    #    channels = pulser.get_channels().asarray
    #    sp = SequencePlotter(hr, channels)
    #    sp.makePlot()
        print 'done'