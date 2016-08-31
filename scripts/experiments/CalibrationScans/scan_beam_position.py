# scan picomotor
from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.rabi_flop_scannable import rabi_flopping_scannable as rf
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import labrad

class scan_beam_position(experiment):

    name = 'ScanBeamPosition'

    required_parameters = [
        ('CalibrationScans', 'position_scan_axis'),
        ('CalibrationScans', 'position_scan_step_size'),
        ('CalibrationScans', 'position_scan_num_steps')
        ]

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(rf.all_required_parameters()))
        parameters = list(parameters)
        return parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.rabi_flop = self.make_experiment(rf)
        self.rabi_flop.initialize(cxn, context, ident)
        self.save_context = cxn.context()
        self.dv = cxn.data_vault
        #self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network

    def generate_scan(self):
        step_size = self.parameters.CalibrationScans.position_scan_step_size
        n_steps = int(self.parameters.CalibrationScans.position_num_steps)
        product = step_size*n_steps
        

        
        
        

    def run(self, cxn, context):
        
        dv_args = {'output_size':self.rabi_flop.excite.output_size,
                   'experiment_name': self.name,
                   'window_name': 'current',
                   'dataset_name': 'beam_position_scan'
                   }
        scan_methods.setup_data_vault(cxn, self.save_context, dv_args)

        picomotor= self.cxn.picomotorserver
        self.picomotor.mark_setpoint()
        axis = self.parameters.CalibrationScans.position_scan_axis
        
        for i,ampl in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            excitation = self.rabi_flop.run(cxn, context)
            if excitation is None: break 
            submission = [ampl['dBm']]
            submission.extend([excitation])
            self.dv.add(submission, context = self.save_context)
            self.update_progress(i)

        self.picomotor.return_to_setpoint()


