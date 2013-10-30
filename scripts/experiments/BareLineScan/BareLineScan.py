from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.PulseSequences.bare_line_scan import bare_line_scan as sequence
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.scriptLibrary.fly_processing import Binner
from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter
import time
from numpy import linspace
from labrad.units import WithUnit
import labrad
import numpy
       
class bare_line_scan(experiment):
    
    name = 'BareLineScan'
    
    required_parameters = [
                           ('BareLineScan','bin_every'),
                           ('BareLineScan','pulse_sequences_per_timetag_transfer'),
                           ('BareLineScan','total_timetag_transfers'),
                           ('BareLineScan','max_timetags_per_transfer'),
                           ('BareLineScan','doppler_cooling_duration'),
                           ('BareLineScan','frequency_scan'),
                           ]
    
    required_parameters.extend(sequence.required_parameters)
    required_parameters.remove(('DopplerCooling','doppler_cooling_duration'))
    # this parameter will get scanned #
    required_parameters.remove(('BareLineScan','frequency_397_pulse'))
    #required_parameters.remove(('BareLineScan','amplitude_397_pulse'))
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = cxn.data_vault
        self.pulser = cxn.pulser
        self.scan = []
        self.timetag_save_context = cxn.context()
        self.binned_save_context = cxn.context()
        self.total_timetag_save_context = cxn.context()
        self.spectrum_save_context = cxn.context()
        self.timetags_since_last_binsave = 0
        self.bin_every = self.parameters.BareLineScan.bin_every
        self.setup_data_vault()
        self.setup_initial_switches()
    
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
        #self.dv.add_parameter('plotLive', True, context = self.total_timetag_save_context)
        #self.dv.add_parameter('Window', ['BareLineScan Timetags Per Transfer'], context = self.total_timetag_save_context)
        
        self.dv.cd(directory , context = self.spectrum_save_context)
        self.dv.new('BareLineSpectrum {}'.format(datasetNameAppend),[('Frequency', 'MHz')],[('Counts','Arb','Arb')], context = self.spectrum_save_context)
        self.dv.add_parameter('plotLive', True, context = self.spectrum_save_context)
        self.dv.add_parameter('Window', ['BareLineScan Spectrum'], context = self.spectrum_save_context)
        
        
        self.dv.cd(directory , context = self.timetag_save_context)
        self.dv.cd(directory , context = self.binned_save_context)
        self.dv.cd(directory , context = self.spectrum_save_context)
        
    def setup_initial_switches(self):

        self.pulser.switch_auto('866DP', True) #high TTL corresponds to light OFF
        self.pulser.switch_manual('crystallization',  False)
        #switch off 729 at the beginning
        self.pulser.output('729DP', False)
    
    # setup frequency scan #
        
    def setup_sequence_parameters(self):
        line_scan = self.parameters.BareLineScan
        #self.parameters['BareLineScan.frequency_397_pulse'] = line_scan.rabi_amplitude_729
        self.parameters['DopplerCooling.doppler_cooling_duration'] = self.parameters.BareLineScan.doppler_cooling_duration
        minim,maxim,steps = line_scan.frequency_scan
        minim = minim['MHz']; maxim = maxim['MHz']
        self.scan = linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'MHz') for pt in self.scan]
        
    def program_pulser(self, frequency_397):
        self.pulser.reset_timetags()
        self.parameters['BareLineScan.frequency_397_pulse'] = frequency_397
        pulse_sequence = sequence(self.parameters)
        pulse_sequence.programSequence(self.pulser)   
        #if not reprogram:
        self.timetag_record_cycle = pulse_sequence.timetag_record_cycle
        self.start_recording_timetags = pulse_sequence.start_recording_timetags
        #print self.timetag_record_cycle
        #print self.start_recording_timetags
            

    def run(self, cxn, context):
        self.setup_sequence_parameters()
        back_to_back = int(self.parameters.BareLineScan.pulse_sequences_per_timetag_transfer)
        total_timetag_transfers = int(self.parameters.BareLineScan.total_timetag_transfers)
        
        for i,frequency_397 in enumerate(self.scan):
            #can stop between different frequency points
            should_stop = self.pause_or_stop()
            if should_stop: break
            
            self.program_pulser(frequency_397)
            self.binner = Binner(self.timetag_record_cycle['s'], 100e-9)
                
            for index in range(total_timetag_transfers): 
                 
                self.pulser.start_number(back_to_back)
                self.pulser.wait_sequence_done()
                self.pulser.stop_sequence()
                #get readout count = # of count from blue pulse
                readouts = self.pulser.get_readout_counts().asarray
                average_readouts = numpy.average(readouts)
                print average_readouts
                print frequency_397
                self.dv.add([frequency_397['MHz'],average_readouts], context = self.spectrum_save_context)
                
                
                #get timetags and save
                timetags = self.pulser.get_timetags().asarray
                #print self.parameter.DopplerCooling.doppler_cooling_duration
                if timetags.size >= self.parameters.BareLineScan.max_timetags_per_transfer:
                    raise Exception("Timetags Overflow, should reduce number of back to back pulse sequences")
                else:
                    self.dv.add([index, timetags.size], context = self.total_timetag_save_context)
                iters = index * numpy.ones_like(timetags)
                self.dv.add(numpy.vstack((iters,timetags)).transpose(), context = self.timetag_save_context)
                
                #collapse the timetags onto a single cycle starting at 0
                timetags = timetags - self.start_recording_timetags['s']
                print self.start_recording_timetags
                #print self.start_recording_timetags
                timetags = timetags % self.timetag_record_cycle['s']
                #print self.start_recording_timetags, self.timetag_record_cycle
                self.binner.add(timetags, back_to_back * self.parameters.BareLineScan.cycles_per_sequence)
                self.timetags_since_last_binsave += timetags.size
                #if self.timetags_since_last_binsave > self.bin_every:
            
            self.save_histogram()
            
                #self.timetags_since_last_binsave = 0
                #self.bin_every *= 2
            self.update_progress(i)
                
    def save_histogram(self, force = False):
        bins, hist = self.binner.getBinned(False)
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        self.dv.new('Binned {}'.format(datasetNameAppend),[('Time', 'us')],[('CountRate','Counts/sec','Counts/sec')], context = self.binned_save_context)
        self.dv.add_parameter('plotLive', True , context = self.binned_save_context)
        self.dv.add_parameter('Window', ['BareLineScan Histogram'], context = self.binned_save_context)
        self.dv.add(numpy.vstack((bins,hist)).transpose(), context = self.binned_save_context)
    
    def finalize(self, cxn, context):
        self.save_parameters(self.dv, cxn, self.cxnlab, self.timetag_save_context)
    
    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.scan)
        self.sc.script_set_progress(self.ident,  progress)
        
    def save_parameters(self, dv, cxn, cxnlab, context):
        measuredDict = dvParameters.measureParameters(cxn, cxnlab)
        dvParameters.saveParameters(dv, measuredDict, context)
        dvParameters.saveParameters(dv, dict(self.parameters), context)          

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = bare_line_scan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)