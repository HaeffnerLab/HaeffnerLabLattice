from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import parity_flop
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace
import numpy as np
from treedict import TreeDict

class vaet_parity_flop(experiment):
    
    name = 'VAETParityFlop'
    trap_frequencies = [
                        ('TrapFrequencies','axial_frequency'),
                        ('TrapFrequencies','radial_frequency_1'),
                        ('TrapFrequencies','radial_frequency_2'),
                        ('TrapFrequencies','rf_drive_frequency'),                       
                        ]
    
    gate_required_parameters = [
                           ('SZX', 'sideband_selection'),
                           ('SZX', 'ac_stark_shift'),
                           ('SZX', 'amp_red'),
                           ('SZX', 'amp_blue'),

                           ('VAET', 'detuning'),
                           ('VAET', 'line_selection'),
                           ('VAET', 'duration_scan'),
                     
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
        parameters = parameters.union(set(parity_flop.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('VAET','duration'))
        parameters.remove(('VAET','frequency'))
        parameters.remove(('GlobalRotation','frequency'))
        parameters.remove(('GlobalRotation','angle'))
        parameters.remove(('MolmerSorensen', 'amplitude'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(parity_flop)
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
        self.load_frequency()
        self.parameters['GlobalRotation.angle'] = WithUnit(np.pi/2, 'rad')
        self.parameters['MolmerSorensen.amplitude'] = WithUnit(-63., 'dBm')
        vaet = self.parameters.VAET
        minim,maxim,steps = vaet.duration_scan
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
        dependents.append( ('Parity', 'Parity', 'Parity'))
        ds=self.dv.new('Parity Flop {}'.format(datasetNameAppend),[('Excitation', 'us')], dependents , context = self.save_context)
        self.dv.add_parameter('Window', ['Parity Flop'], context = self.save_context)
        #self.dv.add_parameter('plotLive', True, context = self.save_context)
        if self.grapher is not None:
            self.grapher.plot_with_axis(ds, 'parity', self.scan)
        
    def load_frequency(self):
        #reloads trap frequencies and gets the latest information from the drift tracker
        self.reload_some_parameters(self.trap_frequencies) 
        ms = self.parameters.MolmerSorensen
        szx = self.parameters.SZX
        vaet = self.parameters.VAET
        # set the double pass to the carrier frequency
        frequency = cm.frequency_from_line_selection('auto', WithUnit(0, 'kHz'), vaet.line_selection, self.drift_tracker)
        print frequency
        #trap = self.parameters.TrapFrequencies

        ####### SET DOUBLE PASSES TO THE CARRIER FREQUENCY ########
        self.parameters['VAET.frequency'] = frequency
        self.parameters['GlobalRotation.frequency'] = frequency
        delta = self.parameters.VAET.detuning

        ## now program the CW dds boards
        # Ok so, because we are stupid the single pass AOMs all use the -1 order
        # so if we make the single pass frequency 81 MHz, we're actually driving -red-
        # of the carrier by 1 MHz. Keep that in mind until we change it.

        szx_mode = szx.sideband_selection
        szx_trap_frequency = self.parameters['TrapFrequencies.' + szx_mode]
        
        ### MOLMER SORENSEN FREQUENCIES AND AMPLITUDES ###

        f_global = WithUnit(80.0, 'MHz') + WithUnit(0.15, 'MHz')
        f_local = WithUnit(80.0, 'MHz') - WithUnit(0.2, 'MHz')

        self.dds_cw.frequency('2', f_global)
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
        
        self.dds_cw.output('5', True) # thermalization
        time.sleep(1.0)

        self.dds_cw.output('5', False)
        time.sleep(0.1) # make sure everything is set before starting the sequence

    def run(self, cxn, context):
        self.setup_sequence_parameters()
        self.setup_data_vault()
        for i,duration in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            self.parameters['VAET.duration'] = duration
            self.excite.set_parameters(self.parameters)
            excitation, readouts = self.excite.run(cxn, context, readout_mode = 'num_excited')
            if excitation is None: break 
            submission = [duration['us']]
            submission.extend(excitation)
            submission.extend( [self.compute_parity_pmt(readouts)])
            self.dv.add(submission, context = self.save_context)
            self.update_progress(i)

    def compute_parity_pmt(self, readouts):
        '''
        computes the parity of the provided readouts using a pmt
        '''
        threshold_low = self.parameters.StateReadout.threshold_list[1][0]
        threshold_high = self.parameters.StateReadout.threshold_list[1][1]
        print "thresholds"
        print threshold_low, threshold_high
        even_parity = np.count_nonzero((readouts <= threshold_low)|(readouts >= threshold_high))
        print "even = ", even_parity
        odd_parity  = np.count_nonzero((readouts >= threshold_low)&(readouts <= threshold_high))
        print "odd = ", odd_parity
        parity = (even_parity - odd_parity)/float(len(readouts))
        return parity
    
    def finalize(self, cxn, context):
        self.save_parameters(self.dv, cxn, self.cxnlab, self.save_context)
        self.excite.finalize(cxn, context)

    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.scan)
        self.sc.script_set_progress(self.ident,  progress)

    def save_parameters(self, dv, cxn, cxnlab, context):
        self.dds_cw.output('5', True)
        measuredDict = dvParameters.measureParameters(cxn, cxnlab)
        dvParameters.saveParameters(dv, measuredDict, context)
        dvParameters.saveParameters(dv, dict(self.parameters), context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = vaet_parity_flop(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)

   