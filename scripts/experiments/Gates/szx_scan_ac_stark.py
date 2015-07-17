from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import  szx_gate
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class szx_scan_ac_stark(experiment):
    
    name = 'SZX_ScanACStark'
    trap_frequencies = [
                        ('TrapFrequencies','axial_frequency'),
                        ('TrapFrequencies','radial_frequency_1'),
                        ('TrapFrequencies','radial_frequency_2'),
                        ('TrapFrequencies','rf_drive_frequency'),                       
                        ]
    gate_required_parameters = [
                           ('SZX','line_selection'),
                           ('SZX','frequency_selection'),
                           ('SZX', 'sideband_selection'),
                           ('SZX', 'detuning'),
                           ('SZX', 'ac_stark_shift_scan'),
                           ('SZX', 'amp_blue'),
                           ('SZX', 'amp_red'),

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
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.gate_required_parameters)
        parameters = parameters.union(set(cls.trap_frequencies))
        parameters = parameters.union(set(szx_gate.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('SZX','frequency'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(molmer_sorensen_gate)
        self.excite.initialize(cxn, context, ident)
        if self.parameters.Crystallization.auto_crystallization:
            self.crystallizer = self.make_experiment(crystallization)
            self.crystallizer.initialize(cxn, context, ident)
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.dds_cw = cxn.dds_cw # connection to the CW dds boards
        self.save_context = cxn.context()
    
    def setup_sequence_parameters(self):
        #self.load_frequency()
        gate = self.parameters.SZX
        #self.parameters['Excitation_729.rabi_excitation_amplitude'] = flop.rabi_amplitude_729
        minim,maxim,steps = gate.ac_stark_shift_scan
        minim = minim['kHz']; maxim = maxim['kHz']
        self.scan = linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'kHz') for pt in self.scan]
        
    def setup_data_vault(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        output_size = self.excite.output_size
        #output_size = 1
        dependants = [('Excitation','Ion {}'.format(ion),'Probability') for ion in range(output_size)]
        self.dv.cd(directory, True,context = self.data_save_context)
        self.dv.new('{0} {1}'.format(self.name, datasetNameAppend),[('Excitation', 'us')], dependants , context = self.data_save_context)
        window_name = self.parameters.get('SZX.window_name', ['SZX_AC_Stark'])
        self.dv.add_parameter('Window', window_name, context = self.data_save_context)
        self.dv.add_parameter('plotLive', True, context = self.data_save_context)
 
    
    def load_frequency(self, ac_stark_shift):
        #reloads trap frequencyies and gets the latest information from the drift tracker
        self.reload_some_parameters(self.trap_frequencies) 
        gate = self.parameters.SZX
        # set the double pass to the carrier frequency
        frequency = cm.frequency_from_line_selection(gate.frequency_selection, gate.manual_frequency_729, gate.line_selection, self.drift_tracker)
        #trap = self.parameters.TrapFrequencies
        self.parameters['SZX.frequency'] = frequency
        
        ## now program the CW dds boards
        # Ok so, because we are stupid the single pass AOMs all use the -1 order
        # so if we make the single pass frequency 81 MHz, we're actually driving -red-
        # of the carrier by 1 MHz. Keep that in mind until we change it.
        mode = gate.sideband_selection
        trap_frequency = self.parameters['TrapFrequencies.' + mode]
        
        freq_blue = WithUnit(80., 'MHz') - trap_frequency/2. - gate.detuning + ac_stark_shift
        freq_red = WithUnit(80., 'MHz') + trap_frequency/2. + ac_stark_shift
        amp = WithUnit(-15., 'dBm') # carrier amplitude
        amp_blue = self.parameters.SZX.amp_blue
        amp_red = self.parameters.SZX.amp_red
        self.dds_cw.frequency('0', freq_blue)
        self.dds_cw.frequency('1', freq_red)
        self.dds_cw.frequency('2', WithUnit(80., 'MHz'))
        self.dds_cw.amplitude('0', amp_blue)
        self.dds_cw.amplitude('1', amp_red)
        self.dds_cw.amplitude('2', amp)
        self.dds_cw.output('0', True)
        self.dds_cw.output('1', True)
        self.dds_cw.output('2', True)
        time.sleep(0.5) # make sure everything is set before starting the sequence
        
    def run(self, cxn, context):
        self.setup_data_vault()
        self.setup_sequence_parameters()
        for i,freq in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            excitation = self.get_excitation_crystallizing(cxn, context, freq)
            if excitation is None: break 
            submission = [freq['kHz']]
            submission.extend(excitation)
            self.dv.add(submission, context = self.save_context)
            self.update_progress(i)
    
    def get_excitation_crystallizing(self, cxn, context, freq):
        # right now don't crystallize because I'm not sure if it works
        excitation = self.do_get_excitation(cxn, context, freq)
        #if self.parameters.Crystallization.auto_crystallization:
        #    initally_melted, got_crystallized = self.crystallizer.run(cxn, context)
        #    #if initially melted, redo the point
        #    while initally_melted:
        #        if not got_crystallized:
        #            #if crystallizer wasn't able to crystallize, then pause and wait for user interaction
        #            self.cxn.scriptscanner.pause_script(self.ident, True)
        #            should_stop = self.pause_or_stop()
        #            if should_stop: return None
        #        excitation = self.do_get_excitation(cxn, context, duration)
        #        initally_melted, got_crystallized = self.crystallizer.run(cxn, context)
        return excitation
    
    def do_get_excitation(self, cxn, context, freq):
        self.load_frequency(freq)
        self.excite.set_parameters(self.parameters)
        exc, readouts = self.excite.run(cxn, context)
        return exc
     
    def finalize(self, cxn, context):
        #self.save_parameters(self.dv, cxn, self.cxnlab, self.rabi_flop_save_context)
        self.excite.finalize(cxn, context)

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
    exprt = szx_scan_ac_stark(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
