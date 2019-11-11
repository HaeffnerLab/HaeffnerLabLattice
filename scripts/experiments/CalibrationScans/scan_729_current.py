from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.rabi_flop_scannable import rabi_flopping_scannable as rf
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import labrad
import time

class scan_729_current(experiment):
    name = 'Scan729_current'
    required_parameters = [('CalibrationScans', 'current_scan'),
                           ('CalibrationScans', 'rabi_detuning'),
                           ('CalibrationScans', 'excitation_time')
                          ]

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(rf.all_required_parameters()))
        parameters = list(parameters)
        parameters.remove( ('RabiFlopping', 'frequency_selection') )
        parameters.remove( ('RabiFlopping', 'manual_frequency_729') )
        parameters.remove( ('RabiFlopping_Sit', 'sit_on_excitation') )
        return parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.rabi_flop = self.make_experiment(rf)
        self.rabi_flop.initialize(cxn, context, ident)
        self.save_context = cxn.context()
        self.dv = cxn.data_vault
        self.dac = self.rabi_flop.cxnlab.laserdac_server

    def get_frequency(self):
        """ We have to fool the rabi flopping experiment to let us put in
            a detuning from the carrier. To do this we caculate the frequency
            we want and then feed this to rabi flopping as a 'manual' frequency
        """
        flop = self.parameters.RabiFlopping
        frequency = cm.frequency_from_line_selection('auto', flop.manual_frequency_729, flop.line_selection, self.drift_tracker)
        frequency = frequency + self.parameters.CalibrationScans.rabi_detuning
        return frequency
        

    def run(self, cxn, context):

        dv_args = {'output_size':self.rabi_flop.excite.output_size,
                   'experiment_name': self.name,
                   'window_name': 'current',
                   'dataset_name': 'injection_current_scan'
                   }
        scan_methods.setup_data_vault(cxn, self.save_context, dv_args)

        scan_param = self.parameters.CalibrationScans.current_scan
        self.scan = scan_methods.simple_scan(scan_param, 'V')
        frequency = self.get_frequency()
        cs = self.parameters.CalibrationScans
        for i, v in  enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            replace = TreeDict.fromdict({
                                     'RabiFlopping.frequency_selection':'manual',
                                     'RabiFlopping.manual_frequency_729':frequency,
                                     'RabiFlopping_Sit.sit_on_excitation': cs.excitation_time,
                                    })
            self.rabi_flop.set_parameters(replace)
            self.dac.set_individual_analog_voltages([('06', v['V'])])
            time.sleep(2) # time to make sure the current gets set from the dac

            excitation = self.rabi_flop.run(cxn, context)
            if excitation is None: break 
            submission = [v['V']]
            submission.extend([excitation])
            self.dv.add(submission, context = self.save_context)
            self.update_progress(i)
            
    def finalize(self, cxn, context):
        self.save_parameters(self.dv, cxn, self.rabi_flop.cxnlab, self.save_context)
        self.rabi_flop.finalize(cxn, context)

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
    exprt = scan_sb_cooling_854(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)            
