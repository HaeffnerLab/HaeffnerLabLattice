from common.abstractdevices.script_scanner.scan_methods import experiment
from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from treedict import TreeDict
from labrad.units import WithUnit
import time

class seq(pulse_sequence):
    required_parameters = []
    
    def sequence(self):
        
        t = WithUnit(500., 'us')
        self.start = self.start + WithUnit(5, 'us')
        self.end = self.start + t
        #ch = 'global397'
        ch = '729DP_1'
        freq = WithUnit(0., 'MHz')
        ampl = WithUnit(-5., 'dBm')
        phase = WithUnit(0, 'deg')
        prof = 0
        self.addDDS(ch, self.start, t, freq, ampl, phase, prof)
        self.start = self.start + WithUnit(2, 'us') + t
        ampl = WithUnit(-5., 'dBm')
        freq = WithUnit(0, 'MHz')
        phase = WithUnit(90, 'deg')
        self.addDDS(ch, self.start, t, freq, ampl, phase, prof)

class test(experiment):
    
    def __init__(self):
        import labrad
        cxn = labrad.connect()
        self.pulser = cxn.pulser
        self.pulse_sequence = seq

    def run(self):
        repetitions = 10
        pulse_sequence = self.pulse_sequence(TreeDict({}))
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_number(repetitions)
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        
if __name__ == '__main__':
    exprt = test()
    for i in range(100):
        exprt.run()
        #time.sleep(0.1)
        