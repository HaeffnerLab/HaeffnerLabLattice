from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.PulseSequences.branching_ratio import branching_ratio as branching_ratio_sequence
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.scriptLibrary.fly_processing import Binner
import time
import numpy
import labrad
       
class branching_ratio(experiment):
    
    name = 'BranchingRatio'
    
    required_parameters = [
                           ('BranchingRatio','bin_every'),
                           ('BranchingRatio','pulse_sequences_per_timetag_transfer'),
                           ('BranchingRatio','total_timetag_transfers'),
                           ('BranchingRatio','max_timetags_per_transfer'),
                           ]
    required_parameters.extend(branching_ratio_sequence.required_parameters)
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = cxn.data_vault
        self.pulser = cxn.pulser
        self.timetag_save_context = cxn.context()
        self.binned_save_context = cxn.context()
        self.total_timetag_save_context = cxn.context()
        self.timetags_since_last_binsave = 0
        self.bin_every = self.parameters.BranchingRatio.bin_every
        self.setup_data_vault()
        self.setup_initial_switches()
        self.program_pulser()
    
    def setup_data_vault(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        self.dv.cd(directory ,True, context = self.timetag_save_context)
        self.dv.new('Timetags {}'.format(datasetNameAppend),[('Time', 'sec')],[('Photons','Arb','Arb')], context = self.timetag_save_context)
        self.dv.cd(directory , context = self.total_timetag_save_context)
        self.dv.new('Total Timetags Per Transfer {}'.format(datasetNameAppend),[('Time', 'sec')],[('Total timetags','Arb','Arb')], context = self.total_timetag_save_context)
        self.dv.add_parameter('plotLive', True, context = self.total_timetag_save_context)
        self.dv.add_parameter('Window', ['BranchingRatio Timetags Per Transfer'], context = self.total_timetag_save_context)
        self.dv.cd(directory , context = self.timetag_save_context)
        self.dv.cd(directory , context = self.binned_save_context)
        
    def setup_initial_switches(self):
        self.pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
        self.pulser.switch_manual('crystallization',  False)
        #switch off 729 at the beginning
        self.pulser.output('729DP', False)
        
    def program_pulser(self):
        self.pulser.reset_timetags()
        pulse_sequence = branching_ratio_sequence(self.parameters)
        pulse_sequence.programSequence(self.pulser)
        self.timetag_record_cycle = pulse_sequence.timetag_record_cycle
        self.start_recording_timetags = pulse_sequence.start_recording_timetags
        self.binner = Binner(self.timetag_record_cycle['s'], 100e-9)

    def run(self, cxn, context):
        back_to_back = int(self.parameters.BranchingRatio.pulse_sequences_per_timetag_transfer)
        total_timetag_transfers = int(self.parameters.BranchingRatio.total_timetag_transfers)
        for index in range(total_timetag_transfers):  
            should_stop = self.pause_or_stop()
            if should_stop: break
            self.pulser.start_number(back_to_back)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            #get timetags and save
            timetags = self.pulser.get_timetags().asarray
            if timetags.size >= self.parameters.BranchingRatio.max_timetags_per_transfer:
                raise Exception("Timetags Overflow, should reduce number of back to back pulse sequences")
            else:
                self.dv.add([index, timetags.size], context = self.total_timetag_save_context)
            iters = index * numpy.ones_like(timetags)
            self.dv.add(numpy.vstack((iters,timetags)).transpose(), context = self.timetag_save_context)
            #collapse the timetags onto a single cycle starting at 0
            timetags = timetags - self.start_recording_timetags['s']
            #print self.start_recording_timetags
            timetags = timetags % self.timetag_record_cycle['s']
            print self.start_recording_timetags, self.timetag_record_cycle
            self.binner.add(timetags, back_to_back * self.parameters.BranchingRatio.cycles_per_sequence)
            self.timetags_since_last_binsave += timetags.size
            if self.timetags_since_last_binsave > self.bin_every:
                self.save_histogram()
                self.timetags_since_last_binsave = 0
                self.bin_every *= 2
            self.update_progress(index)
                
    def save_histogram(self, force = False):
        bins, hist = self.binner.getBinned()
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        self.dv.new('Binned {}'.format(datasetNameAppend),[('Time', 'us')],[('CountRate','Counts/sec','Counts/sec')], context = self.binned_save_context)
        self.dv.add_parameter('plotLive', True , context = self.binned_save_context)
        self.dv.add_parameter('Window', ['BranchingRatio Histogram'], context = self.binned_save_context)
        self.dv.add(numpy.vstack((bins,hist)).transpose(), context = self.binned_save_context)
    
    def finalize(self, cxn, context):
        self.save_parameters(self.dv, cxn, self.cxnlab, self.timetag_save_context)
    
    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / float(self.parameters.BranchingRatio.total_timetag_transfers)
        self.sc.script_set_progress(self.ident,  progress)
        
    def save_parameters(self, dv, cxn, cxnlab, context):
        measuredDict = dvParameters.measureParameters(cxn, cxnlab)
        dvParameters.saveParameters(dv, measuredDict, context)
        dvParameters.saveParameters(dv, dict(self.parameters), context)          

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = branching_ratio(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)