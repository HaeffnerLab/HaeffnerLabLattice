from sequence import Sequence

class sampleReadout(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                    }

    def defineSequence(self):
        pulser = self.pulser
        for i in range(10):
            pulser.add_ttl_pulse('ReadoutCount', 0.0+i/10.0, 0.05)

        
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = sampleReadout(pulser)
    pulser.new_sequence()
    seq.defineSequence()
    pulser.program_sequence()
    pulser.reset_readout_counts()
    #pulser.start_single()
    pulser.start_number(1)
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    counts = pulser.get_readout_counts().asarray
    print counts
    print counts.size
    print 'done'