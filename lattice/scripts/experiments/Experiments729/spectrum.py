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
        self.percentDone = 0.0
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
        self.histogram_save_context = self.cxn.context()
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
        sequence_parameters['doppler_cooling_frequency_866'] = self.check_parameter(self.p.frequency_866)
        
        sequence_parameters['state_readout_frequency_866'] = self.check_parameter(self.p.frequency_866)
        sequence_parameters['state_readout_amplitude_866'] = self.check_parameter(self.p.doppler_cooling_amplitude_866)
        
        sequence_parameters['optical_pumping_continuous_frequency_854'] = self.check_parameter(self.p.frequency_854)
        sequence_parameters['optical_pumping_continuous_amplitude_854'] = self.check_parameter(self.p.optical_pumping_amplitude_854)
        sequence_parameters['optical_pumping_continuous_frequency_729'] = self.check_parameter(self.p.optical_pumping_frequency)
        sequence_parameters['optical_pumping_continuous_amplitude_729'] = self.check_parameter(self.p.optical_pumping_amplitude_729)
        
        sequence_parameters['repump_d_frequency_854'] = self.check_parameter(self.p.frequency_854)
        sequence_parameters['repump_d_amplitude_854'] = self.check_parameter(self.p.amplitude_854)
        
        sequence_parameters['rabi_excitation_amplitude'] = self.check_parameter(self.p.amplitude_729)
        sequence_parameters['rabi_excitation_duration'] = self.check_parameter(self.p.excitation_time)
        
        print 'in sequnece parameters'
        print sequence_parameters['rabi_excitation_amplitude']

        return sequence_parameters
        
    def program_pulser(self, frequency_729, amplitude_729 = None):
        if amplitude_729 is not None:
            print 'overwriting', amplitude_729
            self.sequence_parameters['rabi_excitation_amplitude'] = amplitude_729
        self.sequence_parameters['rabi_excitation_frequency'] = frequency_729
        #filled = [key for key,value in self.sequence_parameters.iteritems() if value is not None]
        #unfilled = [key for key,value in self.sequence_parameters.iteritems() if value is None]
        seq = sequence(**self.sequence_parameters)
        seq.programSequence(self.pulser)

    def sequence(self):
        scan = self.check_parameters(self.p.frequencies)
        repeatitions = int(self.check_parameter(self.p.repeat_each_measurement, keep_units = False))
        threshold = int(self.check_parameter(self.p.readout_threshold, keep_units = False))
        for index, freq in enumerate(scan):
            print 'Frequency {}'.format(freq)
            self.percentDone = 100.0 * index / len(scan)
            should_continue = self.sem.block_experiment(self.experimentPath, self.percentDone)
            if not should_continue:
                print 'Not Continuing'
                return
            else:
                #program pulser, run sequence, and get readouts
                self.program_pulser(freq)
                self.pulser.start_number(repeatitions)
                self.pulser.wait_sequence_done()
                self.pulser.stop_sequence()
                readouts = self.pulser.get_readout_counts().asarray
                #save frequency scan
                perc_excited = numpy.count_nonzero(readouts <= threshold) / float(len(readouts))
                self.dv.add(freq.value, perc_excited)
                #save readout counts
                freqs = numpy.ones_like(readouts) * freq
                self.dv.add(numpy.vstack((freqs, readouts)).transpose(), context = self.readout_save_context)       
                self.total_readouts.extend(readouts)
                self.save_histogram()
        self.percentDone = 100.0
                
    def save_histogram(self, force = False):
        if (len(self.total_readouts) >= 500) or force:
            hist, bins = numpy.histogram(self.total_readouts, 50)
            self.dv.new('Histogram {}'.format(self.datasetNameAppend),[('Counts', 'Arb')],[('Occurence','Arb','Arb')], context = self.histogram_save_context )
            self.dv.add(numpy.vstack((bins[0:-1],hist)).transpose(), context = self.histogram_save_context )
            self.dv.add_parameter('Histogram729', True, context = self.histogram_save_context )
            self.total_readouts = []
    
    def save_parameters(self):
        measuredDict = dvParameters.measureParameters(self.cxn, self.cxnlab)
        dvParameters.saveParameters(self.dv, measuredDict)
        dvParameters.saveParameters(self.dv, self.p.toDict())
    
    def finalize(self):
        self.save_histogram(force = True)
        self.save_parameters()
        self.sem.finish_experiment(self.experimentPath, self.percentDone)
        self.cxn.disconnect()
        self.cxnlab.disconnect()
        print 'Finished: {0}, {1}'.format(self.experimentPath, self.dirappend)        

if __name__ == '__main__':
    exprt = spectrum()
    exprt.run()