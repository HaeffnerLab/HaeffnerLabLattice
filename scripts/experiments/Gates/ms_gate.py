from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import  molmer_sorensen_gate
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class ms_gate(experiment):
    
    name = 'MolmerSorensenGate'
    trap_frequencies = [
                        ('TrapFrequencies','axial_frequency'),
                        ('TrapFrequencies','radial_frequency_1'),
                        ('TrapFrequencies','radial_frequency_2'),
                        ('TrapFrequencies','rf_drive_frequency'),                       
                        ]
    gate_required_parameters = [
                           ('MolmerSorensen','duration_scan'),
                           ('MolmerSorensen','line_selection'),
                           ('MolmerSorensen','frequency_selection'),
                           ('MolmerSorensen', 'sideband_selection'),
                           ('MolmerSorensen', 'detuning'),
                           ('MolmerSorensen', 'ac_stark_shift'),
                           ('MolmerSorensen', 'amp_red'),
                           ('MolmerSorensen', 'amp_blue'),
                           ('MolmerSorensen', 'camera_readout'),

                           ('Crystallization', 'auto_crystallization'),
                           ('Crystallization', 'camera_record_exposure'),
                           ('Crystallization', 'camera_threshold'),
                           ('Crystallization', 'max_attempts'),
                           ('Crystallization', 'max_duration'),
                           ('Crystallization', 'min_duration'),
                           ('Crystallization', 'pmt_record_duration'),
                           ('Crystallization', 'pmt_threshold'),
                           ('Crystallization', 'use_camera'),
                           
                           ('StateReadout', 'camera_readout_duration')
                           ]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.gate_required_parameters)
        parameters = parameters.union(set(cls.trap_frequencies))
        parameters = parameters.union(set(molmer_sorensen_gate.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('MolmerSorensen','frequency'))
        parameters.remove(('LocalRotation','frequency'))
        parameters.remove(('MolmerSorensen','duration'))

        parameters.remove(('StateReadout', 'use_camera_for_readout'))
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
        self.load_frequency()
        gate = self.parameters.MolmerSorensen
        #self.parameters['Excitation_729.rabi_excitation_amplitude'] = flop.rabi_amplitude_729
        minim,maxim,steps = gate.duration_scan
        minim = minim['us']; maxim = maxim['us']
        self.scan = linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'us') for pt in self.scan]
        
    def setup_data_vault(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        self.dv.cd(directory ,True, context = self.save_context)
        dependents = [('NumberExcited',st,'Probability') for st in ['0', '1', '2'] ]
        self.dv.new('MS Gate {}'.format(datasetNameAppend),[('Excitation', 'us')], dependents , context = self.save_context)
        self.dv.add_parameter('Window', ['Molmer-Sorensen Gate'], context = self.save_context)
        self.dv.add_parameter('plotLive', True, context = self.save_context)

    def setup_data_vault_camera(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        self.dv.cd(directory ,True, context = self.save_context)
        dependents = [('State',st,'Probability') for st in ['SS', 'SD', 'DS', 'DD'] ]
        self.dv.new('MS Gate {}'.format(datasetNameAppend),[('Excitation', 'us')], dependents , context = self.save_context)
        self.dv.add_parameter('Window', ['Molmer-Sorensen Gate'], context = self.save_context)
        self.dv.add_parameter('plotLive', True, context = self.save_context)
        
    
    def load_frequency(self):
        #reloads trap frequencyies and gets the latest information from the drift tracker
        self.reload_some_parameters(self.trap_frequencies) 
        gate = self.parameters.MolmerSorensen
        # set the double pass to the carrier frequency
        frequency = cm.frequency_from_line_selection(gate.frequency_selection, gate.manual_frequency_729, gate.line_selection, self.drift_tracker)
        #trap = self.parameters.TrapFrequencies
        self.parameters['MolmerSorensen.frequency'] = frequency
        self.parameters['LocalRotation.frequency'] = frequency
        
        ## now program the CW dds boards
        # Ok so, because we are stupid the single pass AOMs all use the -1 order
        # so if we make the single pass frequency 81 MHz, we're actually driving -red-
        # of the carrier by 1 MHz. Keep that in mind until we change it.
        mode = gate.sideband_selection
        trap_frequency = self.parameters['TrapFrequencies.' + mode]
        
        freq_blue = WithUnit(80., 'MHz') - trap_frequency - gate.detuning + gate.ac_stark_shift
        freq_red = WithUnit(80., 'MHz') + trap_frequency + gate.detuning + gate.ac_stark_shift
        amp = WithUnit(-15., 'dBm')
        amp_blue = self.parameters.MolmerSorensen.amp_blue
        amp_red = self.parameters.MolmerSorensen.amp_red
        self.dds_cw.frequency('0', freq_blue)
        self.dds_cw.frequency('1', freq_red)
        self.dds_cw.frequency('2', WithUnit(80., 'MHz')) # for driving the carrier
        self.dds_cw.amplitude('0', amp_blue)
        self.dds_cw.amplitude('1', amp_red)
        #self.dds_cw.amplitude('2', amp)
        self.dds_cw.output('0', True)
        self.dds_cw.output('1', True)
        self.dds_cw.output('2', True)
        
        self.dds_cw.output('5', False)
        time.sleep(0.5) # just make sure everything is programmed before starting the sequence
        
    def run(self, cxn, context):
        self.setup_data_vault()
        self.setup_sequence_parameters()
        for i,duration in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            excitation = self.get_excitation_crystallizing(cxn, context, duration)
            if excitation is None: break 
            submission = [duration['us']]
            submission.extend(excitation)
            self.dv.add(submission, context = self.save_context)
            self.update_progress(i)
    
    def get_excitation_crystallizing(self, cxn, context, duration):
        # right now don't crystallize because I'm not sure if it works
        excitation = self.do_get_excitation(cxn, context, duration)
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
    
    def do_get_excitation(self, cxn, context, duration):
        self.load_frequency()
        self.parameters['MolmerSorensen.duration'] = duration
        self.excite.set_parameters(self.parameters)
        states, readouts = self.excite.run(cxn, context, readout_mode = 'num_excited')
        print states
        return states
     
    def finalize(self, cxn, context):
        self.dds_cw.output('5', True)
        self.save_parameters(self.dv, cxn, self.cxnlab, self.save_context)
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
    exprt = ms_gate(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
