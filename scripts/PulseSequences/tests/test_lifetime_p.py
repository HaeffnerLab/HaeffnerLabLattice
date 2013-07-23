from labrad.units import WithUnit
from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter
from lattice.scripts.PulseSequences.lifetime_p import lifetime_p

class test_parameters(object):
    
    parameters = {
              ('DopplerCooling', 'doppler_cooling_frequency_397'):WithUnit(90.0, 'MHz'),
              ('DopplerCooling', 'doppler_cooling_amplitude_397'):WithUnit(-15.0, 'dBm'),
              ('DopplerCooling', 'doppler_cooling_frequency_866'):WithUnit(80.0, 'MHz'),
              ('DopplerCooling', 'doppler_cooling_amplitude_866'):WithUnit(-11.0, 'dBm'),
              ('DopplerCooling', 'doppler_cooling_repump_additional'):WithUnit(100, 'us'),
              ('DopplerCooling', 'doppler_cooling_duration'):WithUnit(1.0,'ms'),
              
              ('LifetimeP','cycles_per_sequence'):126,
              ('LifetimeP','between_pulses'):WithUnit(5, 'us'),
              
              ('LifetimeP','frequency_397_pulse'):WithUnit(90.0, 'MHz'),
              ('LifetimeP','duration_397_pulse'):WithUnit(20, 'us'),
              ('LifetimeP','amplitude_397_pulse'):WithUnit(-16.0, 'dBm'),
              
              ('LifetimeP','duration_866_pulse'):WithUnit(10, 'us'),
              ('LifetimeP','amplitude_866_pulse'):WithUnit(-12.0, 'dBm'),
              ('LifetimeP','frequency_866_pulse'):WithUnit(110, 'MHz'),
              }

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
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
    cs = lifetime_p(d)
    cs.programSequence(cxn.pulser)
    dds = cxn.pulser.human_readable_dds()
    ttl = cxn.pulser.human_readable_ttl()
#    print readout
    channels = cxn.pulser.get_channels().asarray
    sp = SequencePlotter(ttl.asarray, dds.aslist, channels)
    sp.makePlot()