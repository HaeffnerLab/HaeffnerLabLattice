from scripts.experiments.SemaphoreExperiment import SemaphoreExperiment
from scripts.PulseSequences.spectrum_rabi import spectrum_rabi as sequence
from scripts.PulseSequences.spectrum_rabi import sample_parameters
from scripts.scriptLibrary import dvParameters
import time
import numpy
       
class spectrum(SemaphoreExperiment):
    
    def __init__(self):
        self.experimentPath = ['729Experiments','Spectrum']

    def run(self):
        self.initialize()
        try:
            self.sequence()
        except Exception,e:
            print 'Had to stop Sequence with error:', e
        finally:
            self.finalize()

    def initialize(self):
        print 'Started: {}'.format(self.experimentPath)
        self.import_labrad()
        self.setup_data_vault()
        self.sequence_parameters = self.setup_sequence_parameters()
        self.setup_pulser()
        self.total_readouts = []
    
    def import_labrad(self):
        import labrad
        self.cxn = cxn = labrad.connect()
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = self.cxn.data_vault
        self.readout_save_context = self.cxn.context()
        self.pulser = self.cxn.pulser
        self.sem = cxn.semaphore
        self.dv = cxn.data_vault
        self.p = self.populate_parameters(self.sem, self.experimentPath)
        
    def setup_data_vault(self):
        localtime = time.localtime()
        self.datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        self.dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend(self.experimentPath)
        directory.extend(self.dirappend)
        self.dv.cd(directory ,True )
        self.dv.new('Spectrum {}'.format(self.datasetNameAppend),[('Freq', 'MHz')],[('Excitation Probability','Arb','Arb')] )
        self.dv.add_parameter('Window', self.p.window_name)
        self.dv.add_parameter('plotLive',self.p.plot_live_parameter)
        self.dv.cd(directory , context = self.readout_save_context)
        self.dv.new('Readout {}'.format(self.datasetNameAppend),[('Freq', 'MHz')],[('Readout Counts','Arb','Arb')], context = self.readout_save_context )
    
    def setup_pulser(self):
        self.pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
        self.pulser.switch_manual('crystallization',  False)
        #switch off 729 at the beginning
        self.pulser.select_dds_channel('729DP')
        self.pulser.output(False)
    
    def setup_sequence_parameters(self):
        #update the sequence parameters with our values
        sequence_parameters = {}.fromkeys(sample_parameters.parameters)
        check = self.check_parameter
        common_values = dict([(key,check(value)) for key,value in self.p.iteritems() if key in sequence_parameters])
        sequence_parameters.update(common_values)
        print self.p.toDict().keys()
        return sequence_parameters
        
    def program_pulser(self, frequency_729, amplitude_729 = None):
        if amplitude_729 is not None:
            self.sequence_parameters['rabi_excitation_amplitude'] = amplitude_729
        self.sequence_parameters['rabi_excitation_frequency'] = frequency_729
        print type(self.sequence_parameters)
        filled = [key for key,value in self.sequence_parameters.iteritems() if value is not None]
        unfilled = [key for key,value in self.sequence_parameters.iteritems() if value is None]
        print 'filled', numpy.array(filled)
        ['rabi_excitation_frequency' 'doppler_cooling_frequency_397'
         'optical_pumping_continuous_duration' 'doppler_cooling_amplitude_397'
         'doppler_cooling_amplitude_866' 'doppler_cooling_frequency_866'
         'optical_pumping_enable' 'doppler_cooling_duration' 'heating_time']
        print 'unfilled',  numpy.array(unfilled)
        ['optical_pumping_continuous_frequency_854' 
         'optical_pumping_continuous_amplitude_729'
         'optical_pumping_continuous_repump_additional'
         'optical_pumping_continuous_amplitude_854'
         'optical_pumping_continuous_frequency_729'
         
         'rabi_excitation_amplitude'
         'rabi_excitation_duration'
         
         'state_readout_amplitude_397' 
          'state_readout_amplitude_866'
         'state_readout_duration'
         'state_readout_frequency_866'
         'state_readout_frequency_397'
         
         'repump_d_duration'
         'repump_d_amplitude_854'
         
          'repump_d_frequency_854'
         
          ]
        raise()
#        seq = sequence(**values)
#        self.pulser.new_sequence()
#        seq.setVariables(**self.seqP.toDict())
#        seq.defineSequence()
#        self.pulser.program_sequence()
#        print freq

    def sequence(self):
        scan = self.check_parameters(self.p.frequencies)
        repeatitions = int(self.check_parameter(self.p.repeat_each_measurement, keep_units = False))
        threshold = int(self.check_parameter(self.p.readout_threshold, keep_units = False))
        for index, freq in enumerate(scan):
            print 'Frequency {}'.format(freq)
            percentDone = 100.0 * index / len(scan)
            should_continue = self.sem.block_experiment(self.experimentPath, percentDone)
            if not should_continue:
                print 'Not Continuing'
                break
            else:
                #program pulser, run sequence, and get readouts
                self.program_pulser(freq)
#                self.pulser.start_number(repeatitions)
#                self.pulser.wait_sequence_done()
#                self.pulser.stop_sequence()
#                readouts = self.pulser.get_readout_counts().asarray
                readouts = numpy.array([1,2,3,100])
                #save frequency scan
                perc_excited = numpy.count_nonzero(readouts <= threshold) / float(len(readouts))
                self.dv.add(freq, perc_excited)
                #save readout counts
                freqs = numpy.ones_like(readouts) * freq
                self.dv.add(numpy.vstack((freqs, readouts)).transpose(), context = self.readout_save_context)       
                self.total_readouts.extend(readouts)
                
    def save_histogram(self):
        hist, bins = numpy.histogram(self.total_readouts, 50)
        self.dv.new('Histogram {}'.format(self.datasetNameAppend),[('Counts', 'Arb')],[('Occurence','Arb','Arb')] )
        self.dv.add(numpy.vstack((bins[0:-1],hist)).transpose())
        self.dv.add_parameter('Histogram729', True)
    
    def save_parameters(self):
        measuredDict = dvParameters.measureParameters(self.cxn, self.cxnlab)
        dvParameters.saveParameters(self.dv, measuredDict)
        dvParameters.saveParameters(self.dv, self.p.toDict())
    
    def finalize(self):
        self.save_histogram()
        self.save_parameters()
        self.sem.finish_experiment(self.experimentPath)
        self.cxn.disconnect()
        self.cxnlab.disconnect()
        print 'Finished: {0}, {1}'.format(self.experimentPath, self.dirappend)

if __name__ == '__main__':
    exprt = spectrum()
    exprt.run()