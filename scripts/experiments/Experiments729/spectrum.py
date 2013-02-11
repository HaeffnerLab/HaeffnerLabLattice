from lattice.scripts.experiments.SemaphoreExperiment import SemaphoreExperiment
from lattice.scripts.PulseSequences.spectrum_rabi import spectrum_rabi as sequence
from lattice.scripts.PulseSequences.spectrum_rabi import sample_parameters
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
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
        self.pulser.output('729DP', False)
    
    def setup_sequence_parameters(self):
        #update the sequence parameters with our values
        sequence_parameters = {}.fromkeys(sample_parameters.parameters)
        check = self.check_parameter
        common_values = dict([(key,check(value)) for key,value in self.p.iteritems() if key in sequence_parameters])
        sequence_parameters.update(common_values)
        sequence_parameters['doppler_cooling_frequency_866'] = check(self.p.frequency_866)
        sequence_parameters['state_readout_frequency_866'] = check(self.p.frequency_866)
        sequence_parameters['optical_pumping_frequency_866'] = check(self.p.frequency_866)
        sequence_parameters['sideband_cooling_frequency_866'] = check(self.p.frequency_866)     
        sequence_parameters['optical_pumping_frequency_854'] = check(self.p.frequency_854)
        sequence_parameters['sideband_cooling_frequency_854'] = check(self.p.frequency_854)
        sequence_parameters['repump_d_frequency_854'] = check(self.p.frequency_854)
        return sequence_parameters
        
    def program_pulser(self, frequency_729, ampl = None, duration = None):
        if ampl is None:
            ampl = self.check_parameter(self.p.spectrum_amplitude_729)
        if duration is None:
            duration = self.check_parameter(self.p.excitation_time)
        self.sequence_parameters['rabi_excitation_amplitude'] = ampl
        self.sequence_parameters['rabi_excitation_frequency'] = frequency_729
        self.sequence_parameters['rabi_excitation_duration'] = duration
        #sideband cooling line selection
        if self.p.sideband_cooling_use_line_selection:
            line_info = self.p.saved_lines_729
            line_selection = self.p.sideband_cooling_line_selection
            sideband_frequencies = {'radial 1': self.check_parameter(self.p.radial_frequency_1),
                                    'radial 2': self.check_parameter(self.p.radial_frequency_2),
                                    'axial': self.check_parameter(self.p.axial_frequency),
                                    'micromotion':self.check_parameter(self.p.rf_drive_frequency),
                                    }
            freq = cm.saved_line_info_to_frequency_complete(line_info, line_selection, sideband_frequencies)
            self.sequence_parameters['sideband_cooling_frequency_729'] =freq
        else:
            self.sequence_parameters['sideband_cooling_frequency_729'] = self.check_parameter(self.p.sideband_cooling_user_selected_frequency_729)
        #optical pumping line selection
        if self.p.optical_pumping_use_saved:
            info = self.p.saved_lines_729
            line_name = self.p.optical_pumping_use_saved_line
            self.sequence_parameters['optical_pumping_frequency_729'] = cm.saved_line_info_to_frequency(info, line_name)
        else:
            self.sequence_parameters['optical_pumping_frequency_729'] = self.check_parameter(self.p.optical_pumping_user_selected_frequency_729)
#        filled = [key for key,value in self.sequence_parameters.iteritems() if value is not None]; print filled
#        unfilled = [key for key,value in self.sequence_parameters.iteritems() if value is None]; print 'unfilled', unfilled
        seq = sequence(**self.sequence_parameters)
        seq.programSequence(self.pulser)

    def sequence(self):
        if self.p.spectrum_use_saved_frequency:
            scan, ampl, duration = cm.saved_line_info_to_scan( self.p.saved_lines_729, self.p.spectrum_saved_frequency)
        else:
            scan = self.check_parameters(self.p.frequencies)
            ampl = None
            duration = None
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
                self.program_pulser(freq, ampl, duration)
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
        self.pulser.clear_dds_lock()
        self.cxn.disconnect()
        self.cxnlab.disconnect()
        print 'Finished: {0}, {1}'.format(self.experimentPath, self.dirappend)        

if __name__ == '__main__':
    exprt = spectrum()
    exprt.run()