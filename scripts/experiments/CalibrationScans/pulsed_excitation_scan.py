from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.rabi_flop_scannable import rabi_flopping_scannable as rf
from lattice.scripts.scriptLibrary.devices import agilent
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import time
import labrad

class pulsed_excitation_scan(experiment):
    name = 'PulsedExcitationScan'    
    required_parameters = [                           
                           #('Motion_Analysis','sideband_selection'),
                           #('Motion_Analysis','sideband_selection_secondary'),
                           ('Motion_Analysis','do_radial1_scan'),
                           ('Motion_Analysis','do_radial2_scan'),
                           ('Motion_Analysis','scan_frequency'),
                           ('Motion_Analysis','excitation_enable'),
                           ('Motion_Analysis','ramsey_detuning')                           
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
        self.pv = cxn.parametervault
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.agi = agilent(cxn)
        
    def run(self, cxn, context):
        scan_param = self.parameters.Motion_Analysis.scan_frequency
        
        
        if self.parameters.Motion_Analysis.do_radial1_scan:
            #mode = self.parameters.Motion_Analysis.sideband_selection
            mode = 'radial_frequency_1'
            self.scan = scan_methods.simple_scan(scan_param, 'MHz', offset = self.parameters['TrapFrequencies.' + mode])
            
            dv_args = {'output_size':self.rabi_flop.excite.output_size,
                              'experiment_name': self.name,
                              'window_name': 'radial1',
                              'dataset_name': 'exc_freq',
                              'axis': self.scan,
                              'send_to_current': True,
                              }
                   
            scan_methods.setup_data_vault(cxn, self.save_context, dv_args)
            
            self.rabi_flop.set_progress_limits(0, 50.0)
            
            for i,f in enumerate(self.scan):
                should_stop = self.pause_or_stop()
                if should_stop: break
                self.agi.set_frequency(f)
                time.sleep(1)                            
                
                replace = TreeDict.fromdict({
                                             'Motion_Analysis.excitation_enable':True,
                                             'RabiFlopping.sideband_selection':[1,0,0,0],
                                             })
                self.rabi_flop.set_parameters(replace)
                excitation = self.rabi_flop.run(cxn, context)
                if excitation is None: break 
                submission = [f['MHz']]
                submission.extend([excitation])
                self.dv.add(submission, context = self.save_context)
                self.update_progress(i)
                
            self.rabi_flop.save_parameters(self.dv, cxn, self.cxnlab, self.save_context)
            self.rabi_flop.finalize(cxn, context)
                   
        # secondary scan
        if self.parameters.Motion_Analysis.do_radial2_scan:
                    
            mode = 'radial_frequency_2'
            self.scan = scan_methods.simple_scan(scan_param, 'MHz', offset = self.parameters['TrapFrequencies.' + mode])        
                    
            dv_args = {'output_size':self.rabi_flop.excite.output_size,
                       'experiment_name': self.name,
                       'window_name': 'radial2',
                       'dataset_name': 'exc_freq',
                       'axis': self.scan,
                       'send_to_current': True,
                       }
        
            scan_methods.setup_data_vault(cxn, self.save_context, dv_args)
            
            self.rabi_flop.set_progress_limits(50.0, 100.0)
                        
            for i,f in enumerate(self.scan):
                should_stop = self.pause_or_stop()
                if should_stop: break
                self.agi.set_frequency(f)
                time.sleep(1)
                                
                replace = TreeDict.fromdict({
                                             'Motion_Analysis.excitation_enable':True,
                                             'RabiFlopping.sideband_selection':[0,1,0,0],
                                             })
                self.rabi_flop.set_parameters(replace)
                excitation = self.rabi_flop.run(cxn, context)
                if excitation is None: break 
                submission = [f['MHz']]
                submission.extend([excitation])
                self.dv.add(submission, context = self.save_context)
                self.update_progress(i)
                
            self.rabi_flop.save_parameters(self.dv, cxn, self.cxnlab, self.save_context)
            self.rabi_flop.finalize(cxn, context)


            
    def finalize(self, cxn, context):
        #self.save_parameters(self.dv, cxn, self.cxnlab, self.save_context)
        #self.rabi_flop.finalize(cxn, context)
        pass

    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.scan)
        self.sc.script_set_progress(self.ident,  progress)
        

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = pulsed_excitation_scan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
