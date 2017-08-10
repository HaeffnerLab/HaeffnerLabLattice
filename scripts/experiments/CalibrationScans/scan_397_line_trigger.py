from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.spectrum import spectrum
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from fitters import peak_fitter
from labrad.units import WithUnit
from treedict import TreeDict
import time
import numpy as np
import labrad

class scan_397_line_trigger(experiment):

    name = 'Scan397LineTrigger'

    required_parameters = [('Spectrum','custom')
                           ]

    # parameters to overwrite
    remove_parameters = [
        ]
        

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(spectrum.all_required_parameters()))
        parameters = list(parameters)
        for p in cls.remove_parameters:
            parameters.remove(p)
        #will be disabling sideband cooling automatically
        return parameters
    
    
    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.spectrum = self.make_experiment(spectrum)
        
        self.spectrum.initialize(cxn, context, ident,use_camera_override = False)
        self.fitter = peak_fitter()
        self.pv = cxn.parametervault
        self.dds_cw = cxn.dds_cw

        self.dv = cxn.data_vault

        self.pulser = cxn.pulser
        
        self.save_context = cxn.context()

        self.sd_tracker = cxn.sd_tracker

        self.linecenter = self.sd_tracker.get_current_line('S-1/2D-5/2')
        self.linecenter = self.linecenter['MHz']

    def run(self, cxn, context):
       
        dv_args = {'output_size': 1,
                    'experiment_name' : self.name,
                    'window_name': 'current',
                    'dataset_name' : 'Line_Trigger_Scan'
                    }

        scan_param = (WithUnit(2.0, 'ms'), WithUnit(16.0, 'ms'), 10)
        
        self.scan = scan_methods.simple_scan(scan_param, 'ms')
        
        scan_methods.setup_data_vault(cxn, self.save_context, dv_args)

        dt = self.parameters.DriftTracker

        original_linetrigger_state = self.pulser.line_trigger_state()
        self.pulser.line_trigger_state(True)

        # save original state of DDS 5
        dds5_state = self.dds_cw.output('5')

        self.dds_cw.output('5', True)
        time.sleep(1)

        for i,line_trigger_time in enumerate(self.scan):

            #'StateReadout.repeat_each_measurement':no_of_repeats,
            replace = TreeDict.fromdict({
                'DopplerCooling.doppler_cooling_duration':line_trigger_time,
                'Spectrum.line_selection':'S-1/2D-5/2',
                'Spectrum.sideband_selection':[0,0,0,0],
                'Spectrum.sensitivity_selection':'custom',
                'StatePreparation.sideband_cooling_enable':False,
                'StatePreparation.optical_pumping_enable':True,
                'Display.relative_frequencies':False,
                'StateReadout.use_camera_for_readout':False
                })

            self.spectrum.set_parameters(self.parameters)
            self.spectrum.set_parameters(replace)
            self.spectrum.set_progress_limits(0.0, 100.0)
        
            fr, ex = self.spectrum.run(cxn, context)

            fr = np.array(fr)
            ex = np.array(ex)
            ex = ex.flatten()
    
            # take the maximum of the line excitation
            try:
                fit_center, rsb_ex, fit_width = self.fitter.fit(fr, ex, return_all_params = True)
            except:
                fit_center = None

            submission = [line_trigger_time['ms']]
            submission.extend([ 1e3 * (fit_center - self.linecenter) ])
            self.dv.add(submission, context = self.save_context)
 

        # resetting DDS5 state
        time.sleep(1)
        #self.dds_cw.output('5', False)
        self.dds_cw.output('5', dds5_state)
        time.sleep(1)

        # set line trigger back to original state
        self.pulser.line_trigger_state(original_linetrigger_state)


    def finalize(self, cxn, context):
        self.spectrum.finalize(cxn, context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = scan_397_line_trigger(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
