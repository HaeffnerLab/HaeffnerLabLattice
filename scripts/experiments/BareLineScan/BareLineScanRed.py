from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.PulseSequences.bare_line_scan import bare_line_scan as sequence
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.scriptLibrary.fly_processing import Binner
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter
import time
from numpy import linspace
from labrad.units import WithUnit
import labrad
import numpy
       
class bare_line_scan_red(experiment):
    
    name = 'BareLineScanRed'
    
    required_parameters = [
                           ('BareLineScan','bin_every'),
                           ('BareLineScan','pulse_sequences_per_timetag_transfer'),
                           ('BareLineScan','total_timetag_transfers'),
                           ('BareLineScan','max_timetags_per_transfer'),
                           ('BareLineScan','doppler_cooling_duration'),
                           ('BareLineScan','frequency_scan'),
                           ('BareLineScan','use_calibrated_power'),
                           ('BareLineScan','calibrated_power_dataset'),
                           
                           ('Crystallization', 'auto_crystallization'),
                           ('Crystallization', 'camera_record_exposure'),
                           ('Crystallization', 'camera_threshold'),
                           ('Crystallization', 'max_attempts'),
                           ('Crystallization', 'max_duration'),
                           ('Crystallization', 'min_duration'),
                           ('Crystallization', 'pmt_record_duration'),
                           ('Crystallization', 'pmt_threshold'),
                           ('Crystallization', 'use_camera'),
                           
                           ]
    
    required_parameters.extend(sequence.all_required_parameters())
    required_parameters.remove(('DopplerCooling','doppler_cooling_duration'))
    # this parameter will get scanned #
    required_parameters.remove(('BareLineScan','frequency_866_pulse'))
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = cxn.data_vault
        self.pulser = cxn.pulser
        self.scan = []
        self.spectrum_counts = []
        self.use_calibrated_power = self.parameters.BareLineScan.use_calibrated_power
        self.calibrated_power_dataset = int(self.parameters.BareLineScan.calibrated_power_dataset)
        self.timetag_save_context = cxn.context()
        self.binned_save_context = cxn.context()
        self.total_timetag_save_context = cxn.context()
        self.spectrum_save_context = cxn.context()
        self.load_calibrated_power_context = cxn.context()
        self.timetags_since_last_binsave = 0
        self.bin_every = self.parameters.BareLineScan.bin_every
        self.setup_data_vault()
        self.setup_initial_switches()
        self.show_histogram = True
        if self.parameters.Crystallization.auto_crystallization:
            self.crystallizer = self.make_experiment(crystallization)
            self.crystallizer.initialize(cxn, context, ident)
    
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
        self.scan_no_unit = linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'MHz') for pt in self.scan_no_unit]
        
    def program_pulser(self, frequency_866,amplitude_866):
        self.pulser.reset_timetags()
        self.parameters['BareLineScan.frequency_866_pulse'] = frequency_866
        self.parameters['BareLineScan.amplitude_866_pulse'] = amplitude_866
        pulse_sequence = sequence(self.parameters)
        pulse_sequence.programSequence(self.pulser)   
        self.timetag_record_cycle = pulse_sequence.timetag_record_cycle
        self.start_recording_timetags = pulse_sequence.start_recording_timetags

    def get_spectrum_count_crystallizing(self, cxn, context, freq, power):
        count = self.get_spectrum_count(freq,power)
        if self.parameters.Crystallization.auto_crystallization:
            initally_melted, got_crystallized = self.crystallizer.run(cxn, context)
            #if initially melted, redo the point
            while initally_melted:
                if not got_crystallized:
                    #if crystallizer wasn't able to crystallize, then pause and wait for user interaction
                    self.cxn.scriptscanner.pause_script(self.ident, True)
                    should_stop = self.pause_or_stop()
                    if should_stop: return None
                count = self.get_spectrum_count(freq,power)
                initally_melted, got_crystallized = self.crystallizer.run(cxn, context)
        return count
    
    def get_spectrum_count(self, freq, power):
        back_to_back = int(self.parameters.BareLineScan.pulse_sequences_per_timetag_transfer)
        total_timetag_transfers = int(self.parameters.BareLineScan.total_timetag_transfers)
        
        self.program_pulser(freq,power)
        self.binner = Binner(self.timetag_record_cycle['s'], 100e-9)
        
        for index in range(total_timetag_transfers):                
            self.pulser.start_number(back_to_back)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
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
            
            red_duration = self.parameters['BareLineScan.duration_866_pulse']['s']
            blue_duration = self.parameters['BareLineScan.duration_397_pulse']['s']
            gap_duration = self.parameters['BareLineScan.between_pulses']['s']
            
            timetags = timetags - self.start_recording_timetags['s'] - gap_duration - blue_duration ## shift zero to right before 866 peak
            timetags = timetags % self.timetag_record_cycle['s']
            self.binner.add(timetags, back_to_back * self.parameters.BareLineScan.cycles_per_sequence)

            count = self.binner.getCount(gap_duration,2.0*gap_duration+red_duration)
        
        return count
        


    def run(self, cxn, context):
        self.setup_sequence_parameters()
        #calibrated_power=numpy.array([-16.96875,-17.2109375,  -17.59765625, -17.7265625 , -17.6953125, -17.49609375 ,-16.2890625,  -15.20703125 ,-14.64453125 ,-12.125])
        
        if self.use_calibrated_power:
            self.dv.cd(['','QuickMeasurements'] ,True, context = self.load_calibrated_power_context)
            data_set_number = int(self.calibrated_power_dataset)
            self.dv.open(data_set_number, context = self.load_calibrated_power_context)         
            data = self.dv.get(context = self.load_calibrated_power_context).asarray
            calibrated_power = data[:,1]
        else:
            amplitude_866=self.parameters['BareLineScan.amplitude_866_pulse']
            calibrated_power = amplitude_866['dBm']*numpy.ones_like(self.scan_no_unit)
        
        #calibrated_power=numpy.array([-23.8203125, -23.8203125, -24.0703125, -24.0390625, -23.8828125, -23.6640625, -22.3515625, -21.203125,  -20.7421875, -18.2265625])
        for i,frequency_866 in enumerate(self.scan):
            #can stop between different frequency points
            should_stop = self.pause_or_stop()
            if should_stop: break
            
            count = self.get_spectrum_count_crystallizing(cxn,context,frequency_866,WithUnit(calibrated_power[i],'dBm'))

            self.dv.add([frequency_866['MHz'],count], context = self.spectrum_save_context)
            
            if self.show_histogram:
                self.save_histogram()

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
    exprt = bare_line_scan_red(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)