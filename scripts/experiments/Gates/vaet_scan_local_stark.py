from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import vaet
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class vaet_scan_local_stark(experiment):
    
    name = 'VAET_ScanLocalStarkAmplitude'
    trap_frequencies = [
                        ('TrapFrequencies','axial_frequency'),
                        ('TrapFrequencies','radial_frequency_1'),
                        ('TrapFrequencies','radial_frequency_2'),
                        ('TrapFrequencies','rf_drive_frequency'),                       
                        ]
    gate_required_parameters = [
                           ('MolmerSorensen', 'sideband_selection'),
                           ('MolmerSorensen', 'detuning'),
                           ('MolmerSorensen', 'ac_stark_shift'),
                           ('MolmerSorensen', 'amp_red'),
                           ('MolmerSorensen', 'amp_blue'),

                           ('SZX', 'sideband_selection'),
                           ('SZX', 'ac_stark_shift'),
                           ('SZX', 'amp_red'),
                           ('SZX', 'amp_blue'),

                           ('VAET', 'detuning'),
                           ('VAET', 'line_selection'),

                           ('LocalStarkShift', 'scan'),

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
        parameters = parameters.union(set(vaet.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('VAET','frequency'))
        parameters.remove(('LocalRotation','frequency'))
        return parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(vaet)
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
        try:
            self.grapher = cxn.grapher
        except: self.grapher = None
    
    def setup_sequence_parameters(self):
        minim,maxim,steps = self.parameters.LocalStarkShift.scan
        minim = minim['dBm']; maxim = maxim['dBm']
        self.scan = linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'dBm') for pt in self.scan]

    def setup_data_vault(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        self.dv.cd(directory ,True, context = self.save_context)
        dependents = [('NumberExcited',st,'Probability') for st in ['0', '1', '2'] ]
        ds=self.dv.new('VAET Scan {}'.format(datasetNameAppend),[('Excitation', 'kHz')], dependents , context = self.save_context)
        self.dv.add_parameter('Window', ['Local AC Stark Amplitude'], context = self.save_context)
        self.dv.add_parameter('plotLive', True, context = self.save_context)
        if self.grapher is not None:
            self.grapher.plot_with_axis(ds, 'local_stark', self.scan)
    

    def load_frequency(self):
        #reloads trap frequencyies and gets the latest information from the drift tracker
        self.reload_some_parameters(self.trap_frequencies) 
        ms = self.parameters.MolmerSorensen
        szx = self.parameters.SZX
        vaet = self.parameters.VAET
        # set the double pass to the carrier frequency
        frequency = cm.frequency_from_line_selection('auto', WithUnit(0, 'kHz'), vaet.line_selection, self.drift_tracker)
        self.parameters['VAET.frequency'] = frequency
        self.parameters['LocalRotation.frequency'] = frequency
        delta = vaet.detuning
        ## now program the CW dds boards
        # Ok so, because we are stupid the single pass AOMs all use the -1 order
        # so if we make the single pass frequency 81 MHz, we're actually driving -red-
        # of the carrier by 1 MHz. Keep that in mind until we change it.
        ms_mode = ms.sideband_selection
        ms_trap_frequency = self.parameters['TrapFrequencies.' + ms_mode]
        szx_mode = szx.sideband_selection
        szx_trap_frequency = self.parameters['TrapFrequencies.' + szx_mode]
        
        ### MOLMER SORENSEN FREQUENCIES AND AMPLITUDES ###

        f_global = WithUnit(80.0, 'MHz') + WithUnit(0.15, 'MHz')
        f_local = WithUnit(80.0, 'MHz') - WithUnit(0.2, 'MHz')

        freq_blue = f_global - ms_trap_frequency - ms.detuning + ms.ac_stark_shift
        freq_red = f_global + ms_trap_frequency + ms.detuning + ms.ac_stark_shift
        amp_blue = self.parameters.MolmerSorensen.amp_blue
        amp_red = self.parameters.MolmerSorensen.amp_red
        self.dds_cw.frequency('0', freq_blue)
        self.dds_cw.frequency('1', freq_red)
        self.dds_cw.frequency('2', f_global)
        self.dds_cw.amplitude('0', amp_blue)
        self.dds_cw.amplitude('1', amp_red)

        ####### SZX PARAMETERS ##########

        freq_blue = f_local - szx_trap_frequency/2. - delta + szx.ac_stark_shift
        freq_red = f_local + szx_trap_frequency/2. + szx.ac_stark_shift
        amp_blue = self.parameters.SZX.amp_blue
        amp_red = self.parameters.SZX.amp_red
        self.dds_cw.frequency('3', freq_blue)
        self.dds_cw.frequency('4', freq_red)
        self.dds_cw.frequency('5', f_local)
        self.dds_cw.amplitude('3', amp_blue)
        self.dds_cw.amplitude('4', amp_red)

        [self.dds_cw.output(ch, True) for ch in ['0', '1', '2', '3', '4']]

        self.dds_cw.output('5', True) # time to thermalize SP
        time.sleep(1.0)
        self.dds_cw.output('5', False)
        time.sleep(0.1) # make sure everything is set before starting the sequence
        
    def run(self, cxn, context):
        self.setup_sequence_parameters()
        self.setup_data_vault()
        for i,amp in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            excitation = self.get_excitation_crystallizing(cxn, context, amp)
            if excitation is None: break 
            submission = [amp['dBm']]
            submission.extend(excitation)
            self.dv.add(submission, context = self.save_context)
            self.update_progress(i)

    def get_excitation_crystallizing(self, cxn, context, amp):
        # right now don't crystallize because I'm not sure if it works
        excitation = self.do_get_excitation(cxn, context, amp)
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
    
    def do_get_excitation(self, cxn, context, amp):
        self.load_frequency()
        self.parameters['LocalStarkShift.amplitude'] = amp
        self.excite.set_parameters(self.parameters)
        states, readouts = self.excite.run(cxn, context, readout_mode = 'num_excited')
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
    exprt = vaet_scan_local_stark(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
