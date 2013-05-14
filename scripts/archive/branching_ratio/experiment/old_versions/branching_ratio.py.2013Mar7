from lattice.scripts.experiments.SemaphoreExperiment import SemaphoreExperiment
from lattice.scripts.PulseSequences.branching_ratio import branching_ratio as sequence
from lattice.scripts.PulseSequences.branching_ratio import sample_parameters
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.scriptLibrary.fly_processing import Binner
import time
import numpy
       
class branching_ratio(SemaphoreExperiment):
    
    def __init__(self):
        self.experimentPath = ['BranchingRatio']

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
        self.binner = Binner(self.timetag_record_cycle, 100e-9)
        self.timetags_since_last_binsave = 0
        self.save_timetags_every = 25000
        self.save_parameters()
    
    def import_labrad(self):
        import labrad
        self.cxn = cxn = labrad.connect()
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = self.cxn.data_vault
        self.binned_save_context = self.cxn.context()
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
        self.dv.new('Timetags {}'.format(self.datasetNameAppend),[('Iter', 'Arb')],[('Timetags','Sec','Sec')] )
        self.dv.cd(directory , context = self.binned_save_context)
        
    def setup_pulser(self):
        self.pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
        self.pulser.switch_manual('crystallization',  False)
        self.program_pulser()
        self.pulser.reset_timetags()
    
    def setup_sequence_parameters(self):
        #update the sequence parameters with our values
        sequence_parameters = {}.fromkeys(sample_parameters.parameters)
        check = self.check_parameter
        common_values = dict([(key,check(value)) for key,value in self.p.iteritems() if key in sequence_parameters])
        sequence_parameters.update(common_values)
        freq_866 = self.check_parameter(self.p.frequency_866)
        sequence_parameters['doppler_cooling_frequency_866'] = freq_866
        sequence_parameters['frequency_866_pulse'] = freq_866
        return sequence_parameters
        
    def program_pulser(self):
        seq = sequence(**self.sequence_parameters)
        seq.programSequence(self.pulser)
        self.timetag_record_cycle = seq.timetag_record_cycle['s']
        self.start_recording_timetags = seq.start_recording_timetags['s']

    def sequence(self):
        sequences_back_to_back = int(self.check_parameter(self.p.sequences_back_to_back, keep_units = False))
        total_cycles = int(self.check_parameter(self.p.total_cycles, keep_units = False))
        cycles_per_sequence = int(self.sequence_parameters['cycles_per_sequence'].value)
        cycles_per_timetags_transfer = cycles_per_sequence * sequences_back_to_back
        transfers = int(total_cycles / float(cycles_per_timetags_transfer))
        #make sure do at least one transfer
        transfers = max(transfers, 1)
        self.dv.add_parameter('transfers', transfers)
        for index in range(transfers):  
            self.percentDone = 100.0 * index / float(transfers)
            should_continue = self.sem.block_experiment(self.experimentPath, self.percentDone)
            if not should_continue:
                print 'Not Continuing'
                return
            else:
                #run back to back sequences
                self.pulser.start_number(sequences_back_to_back)
                self.pulser.wait_sequence_done()
                self.pulser.stop_sequence()
                #get timetags and save
                timetags = self.pulser.get_timetags().asarray
                if timetags.size >= 32767:
                    raise Exception("Timetags Overflow, should reduce number of back to back pulse sequences")
                iters = index * numpy.ones_like(timetags)
                #save timetags as we get them
                self.dv.add(numpy.vstack((iters,timetags)).transpose())
                #collapse the timetags onto a single cycle starting at 0
                timetags = timetags - self.start_recording_timetags
                timetags = timetags % self.timetag_record_cycle
                self.binner.add(timetags, sequences_back_to_back * cycles_per_sequence)
                print 'saved {} timetags'.format(len(timetags))
                self.timetags_since_last_binsave += timetags.size
                if self.timetags_since_last_binsave > self.save_timetags_every:
                    self.save_histogram()
                    self.timetags_since_last_binsave = 0
                    self.save_timetags_every *= 2
        self.percentDone = 100.0
                
    def save_histogram(self, force = False):
        bins, hist = self.binner.getBinned()
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        self.dv.new('Binned {}'.format(datasetNameAppend),[('Time', 'us')],[('CountRate','Counts/sec','Counts/sec')], context = self.binned_save_context )
        self.dv.add_parameter('plotLive',self.p.plot_live_parameter, context = self.binned_save_context)
        self.dv.add_parameter('Window', self.p.window_name, context = self.binned_save_context)
        self.dv.add(numpy.vstack((bins,hist)).transpose(), context = self.binned_save_context )
    
    def save_parameters(self):
        measuredDict = dvParameters.measureParameters(self.cxn, self.cxnlab)
        dvParameters.saveParameters(self.dv, {'start_recording_timetags':self.start_recording_timetags})
        dvParameters.saveParameters(self.dv, {'timetag_record_cycle':self.timetag_record_cycle})
        dvParameters.saveParameters(self.dv, measuredDict)
        dvParameters.saveParameters(self.dv, self.p.toDict())
    
    def finalize(self):
        self.sem.finish_experiment(self.experimentPath, self.percentDone)
        self.cxn.disconnect()
        self.cxnlab.disconnect()
        print 'Finished: {0}, {1}'.format(self.experimentPath, self.dirappend)        

if __name__ == '__main__':
    exprt = branching_ratio()
    exprt.run()