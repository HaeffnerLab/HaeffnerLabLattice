from labrad.units import WithUnit
from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter
from lattice.scripts.PulseSequences.branching_ratio import branching_ratio

class test_parameters(object):
    
    parameters = {
              ('DopplerCooling', 'doppler_cooling_frequency_397'):WithUnit(110.0, 'MHz'),
              ('DopplerCooling', 'doppler_cooling_amplitude_397'):WithUnit(-11.0, 'dBm'),
              ('DopplerCooling', 'doppler_cooling_frequency_866'):WithUnit(80.0, 'MHz'),
              ('DopplerCooling', 'doppler_cooling_amplitude_866'):WithUnit(-11.0, 'dBm'),
              ('DopplerCooling', 'doppler_cooling_repump_additional'):WithUnit(100, 'us'),
              ('DopplerCooling', 'doppler_cooling_duration'):WithUnit(1.0,'ms'),
              
              ('BranchingRatio','cycles_per_sequence'):50.0,
              ('BranchingRatio','between_pulses'):WithUnit(5, 'us'),
              ('BranchingRatio','duration_397_pulse_1'):WithUnit(20, 'us'),
              ('BranchingRatio','duration_397_pulse_2'):WithUnit(10, 'us'),
              ('BranchingRatio','duration_866_pulse'):WithUnit(10, 'us'),
              ('BranchingRatio','amplitude_866_pulse'):WithUnit(-3.0, 'dBm'),
              ('BranchingRatio','amplitude_397_pulse_1'):WithUnit(-16.0, 'dBm'),
              ('BranchingRatio','amplitude_397_pulse_2'):WithUnit(-11.0, 'dBm'),
              }

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    import time
    from treedict import TreeDict
    params = test_parameters.parameters
    d = TreeDict()
    #make a treedictionary out of the parameters
    for (collection,param), value in test_parameters.parameters.iteritems():
        d['{0}.{1}'.format(collection, param)] = value
#        if not (collection,param) in branching_ratio.required_parameters:
#            print 'parameter not listed among requirments', collection, param
#    for key in d.keys():
#        a = TreeDict()
#        a.update(d)
#        a.pop(key)
#        try:
#            sequence = branching_ratio(a)
#        except Exception:
#            pass
#        else:
#            print 'key not needed', key
    cs = branching_ratio(d)
    cs.programSequence(cxn.pulser)
    dds = cxn.pulser.human_readable_dds()
    ttl = cxn.pulser.human_readable_ttl()
#    print readout
    channels = cxn.pulser.get_channels().asarray
    sp = SequencePlotter(ttl.asarray, dds.aslist, channels)
    sp.makePlot()