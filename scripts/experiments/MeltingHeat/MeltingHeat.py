from lattice.scripts.experiments.SemaphoreExperiment import SemaphoreExperiment
from lattice.scripts.PulseSequences.melting_heat import melting_heat as sequence
from lattice.scripts.PulseSequences.melting_heat import sample_parameters
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.scriptLibrary.crystallizer import Crystallizer
from lattice.scripts.scriptLibrary.fly_processing import Binner, Splicer
import time
import numpy

class MeltingHeat(SemaphoreExperiment):
      
    def __init__(self):
        self.experimentPath = ['MeltingHeat']
        self.experimentPath_heating = ['729Experiments','BlueHeating']

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
        self.crystallizer = Crystallizer(self.pulser, self.pmtflow)
        self.binner = None
    
    def import_labrad(self):
        import labrad
        self.cxn = cxn = labrad.connect()
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = self.cxn.data_vault
        self.binned_save_context = self.cxn.context()
        self.histogram_save_context = self.cxn.context()
        self.pulser = self.cxn.pulser
        self.pulser.clear_dds_lock()
        self.sem = cxn.semaphore
        self.dv = cxn.data_vault
        self.pmtflow = cxn.normalpmtflow
        self.p = self.populate_parameters(self.sem, self.experimentPath)
        self.p_heat = self.populate_parameters(self.sem, self.experimentPath_heating)
    
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
        get_from_heating =[
                           'blue_heating_delay_before', 
                           'blue_heating_delay_after', 
                           'blue_heating_repump_additional', 
                           'local_blue_heating_amplitude_397', 
                           'local_blue_heating_frequency_397',
                           'use_local_blue_heating',
                           'blue_heating_duration',
                           'global_blue_heating_frequency_397',
                           'global_blue_heating_amplitude_397',
                           ]
        common_values_heat = dict([(key,check(value)) for key,value in self.p_heat.iteritems() if key in sequence_parameters])
        common_values = dict([(key,check(value)) for key,value in self.p.iteritems() if key in sequence_parameters])
        for name in get_from_heating:
            sequence_parameters[name] = common_values_heat[name]
        sequence_parameters.update(common_values)        
        sequence_parameters['doppler_cooling_frequency_866'] = self.check_parameter(self.p.frequency_866)
        sequence_parameters['state_readout_frequency_866'] = self.check_parameter(self.p.frequency_866)
        sequence_parameters['blue_heating_frequency_866'] = self.check_parameter(self.p.frequency_866)        
        sequence_parameters['blue_heating_amplitude_866'] = self.check_parameter(self.p.doppler_cooling_amplitude_866)
        
        self.threshold = int(self.check_parameter(self.p.readout_threshold, keep_units = False))
        return sequence_parameters

    def program_pulser(self):
#        filled = [key for key,value in self.sequence_parameters.iteritems() if value is not None]; print filled
#        unfilled = [key for key,value in self.sequence_parameters.iteritems() if value is None]; print unfilled
        seq = sequence(**self.sequence_parameters)
        seq.programSequence(self.pulser)
        if self.binner is None:
            self.binner = Binner(seq.timetag_record_duration['s'], 100.0e-6, offset = seq.start_record_timetags['s'])
    
    def setup_data_vault(self):
        localtime = time.localtime()
        self.datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        self.dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend(self.experimentPath)
        directory.extend(self.dirappend)
        #timetag saving
        self.dv.cd(directory ,True )
        self.dv.new('timetags {}'.format(self.datasetNameAppend),[('Iteration', 'Arb')],[('Timetags','sec','sec')] )
        #binned saving
        self.dv.cd(directory , context = self.binned_save_context)
        self.dv.new('Binned Fluorescence {}'.format(self.datasetNameAppend),[('Time', 'sec')],[('Counts','Arb','Arb')], context = self.binned_save_context )
        self.dv.add_parameter('Window', ['Melting Heat Binned Fluorescence'], context = self.binned_save_context)
        self.dv.add_parameter('plotLive',True, context = self.binned_save_context)
        #histogram saving
        self.dv.cd(directory , context = self.histogram_save_context)
        self.dv.new('Readout Histogram {}'.format(self.datasetNameAppend),[('Counts', 'Arb')],[('Occurence','Arb','Arb')], context = self.histogram_save_context )
        self.dv.add_parameter('Window', ['Melting Heat Readout Histogram'], context = self.histogram_save_context)
        self.dv.add_parameter('plotLive', True, context = self.histogram_save_context)
    
    def save_parameters(self):
        measuredDict = dvParameters.measureParameters(self.cxn, self.cxnlab)
        dvParameters.saveParameters(self.dv, measuredDict)
        dvParameters.saveParameters(self.dv, self.p.toDict())
    
    def sequence(self):
        repeatitions = int(self.check_parameter(self.p.repeat_each_measurement, keep_units = False))
        self.crystallizer.get_initial_rate()
        for repeat in range(repeatitions):
            print 'Repeatition {}'.format(repeat)
            self.percentDone = 100.0 * repeat / float(repeatitions)
            should_continue = self.sem.block_experiment(self.experimentPath, self.percentDone)
            if not should_continue:
                print 'Not Continuing'
                return
            else:
                #run sequence, and get readouts
                self.program_pulser()
                self.pulser.start_number(1)
                self.pulser.wait_sequence_done()
                self.pulser.stop_sequence()
                readouts = self.pulser.get_readout_counts().asarray
                timetags = self.pulser.get_timetags().asarray
                print readouts
                if not self.crystallizer.auto_crystallize():
                    raise Exception("Can't Crystalize")
                self.binner.add(timetags, 1)
                self.total_readouts.extend(readouts)
                #save timetags
                indexes = numpy.ones_like(timetags) * repeat
                self.dv.add(numpy.vstack((indexes, timetags)).transpose())       
        self.percentDone = 100.0
    
    def save_binned(self):
        binned_x, binned_y = self.binner.getBinned(normalize = True)
        self.dv.add(numpy.vstack((binned_x,binned_y)).transpose(), context = self.binned_save_context)
    
    def save_histogram(self):
        if not len(self.total_readouts): return 
        readouts = numpy.array(self.total_readouts)
        perc_excited = numpy.count_nonzero(readouts <= self.threshold) / float(len(readouts))
        print '{0:.1f}% of samples are Melted, below threshold of {1} '.format(100 * perc_excited, self.threshold)
        print '{0:.1f}% of samples are Crystallized, above threshold of {1} '.format(100 * (1 - perc_excited) ,self.threshold)
        hist, bins = numpy.histogram(self.total_readouts, 50)
        self.dv.add(numpy.vstack((bins[0:-1],hist)).transpose(), context = self.histogram_save_context )
            
    def finalize(self):
        self.save_histogram()
        self.save_binned()
        self.save_parameters()
        self.sem.finish_experiment(self.experimentPath, self.percentDone)
        self.pulser.clear_dds_lock()
        self.cxn.disconnect()
        self.cxnlab.disconnect()
        print 'Finished: {0}, {1}'.format(self.experimentPath, self.dirappend)
        
if __name__ == '__main__':
    exprt = MeltingHeat()
    exprt.run()