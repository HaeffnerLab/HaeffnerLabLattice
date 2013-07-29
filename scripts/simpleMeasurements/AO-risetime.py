from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
from treedict import TreeDict
import numpy
from matplotlib import pyplot

class sampleDDS(pulse_sequence):
    
    def sequence(self):
        self.addTTL('866DP', WithUnit(1, 'us'), WithUnit(10,'us'))
        self.addTTL('TimeResolvedCount', WithUnit(1, 'us'), WithUnit(2.0, 'us') )
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    cs = sampleDDS(TreeDict())
    cs.programSequence(cxn.pulser)
    timetags = numpy.array([])
    for i in range(100):
        print i
        cxn.pulser.start_number(30000)
        cxn.pulser.wait_sequence_done()
        cxn.pulser.stop_sequence()
        new_timetags =  cxn.pulser.get_timetags().asarray
        timetags = numpy.append(timetags, new_timetags)
        print timetags.size
    bins = numpy.arange(1e-6, 2e-6, 10e-9)
    print bins
    pyplot.hist(timetags, bins = bins)
    pyplot.show()
    print 'DONE'