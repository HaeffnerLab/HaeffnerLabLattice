from common.abstractdevices.script_scanner.scan_methods import experiment
from drift_tracker_ramsey_oneline import drift_tracker_ramsey_oneline
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np

class drift_tracker_ramsey(experiment):
    
    name = 'DriftTrackerRamsey'
    dt_required_parameters = [
                           ('DriftTracker','line_selection_1'),
                           ('DriftTracker','line_selection_2'),
                           ('DriftTrackerRamsey','line_1_pi_time'),
                           ('DriftTrackerRamsey','line_1_amplitude'),
                           ('DriftTrackerRamsey','line_2_pi_time'),
                           ('DriftTrackerRamsey','line_2_amplitude'),
                           ('DriftTrackerRamsey','error_sensitivity'),
                           ('DriftTrackerRamsey','use_camera_for_readout'),
                           ]

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.dt_required_parameters)
        parameters = parameters.union(set(drift_tracker_ramsey_oneline.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('DriftTrackerRamsey','line_selection'))
        parameters.remove(('DriftTrackerRamsey','pi_time'))
        parameters.remove(('DriftTrackerRamsey','amplitude'))
        parameters.remove(('DriftTrackerRamsey','detuning'))
        return parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.ramsey_dt = self.make_experiment(drift_tracker_ramsey_oneline)
        self.ramsey_dt.initialize(cxn, context, ident)
        self.dds_cw = cxn.dds_cw
        
    def run(self, cxn, context):
        import time
        dds5_state = self.dds_cw.output('5')

        self.dds_cw.output('5', True)
        time.sleep(1)
        dt = self.parameters.DriftTracker
        ramsey_dt = self.parameters.DriftTrackerRamsey
        if dt.line_selection_1 == dt.line_selection_2:
            raise Exception ("The two Drift Tracking lines can not be the same")
        replace_1 = TreeDict.fromdict({
                                       'DriftTrackerRamsey.line_selection':dt.line_selection_1,
                                       'DriftTrackerRamsey.pi_time':ramsey_dt.line_1_pi_time,
                                       'DriftTrackerRamsey.amplitude':ramsey_dt.line_1_amplitude,
                                       'DriftTrackerRamsey.detuning':WithUnit(0,'Hz'),
                                       'StateReadout.use_camera_for_readout':ramsey_dt.use_camera_for_readout,
                                       })
        replace_2 = TreeDict.fromdict({
                                       'DriftTrackerRamsey.line_selection':dt.line_selection_2,
                                       'DriftTrackerRamsey.pi_time':ramsey_dt.line_2_pi_time,
                                       'DriftTrackerRamsey.amplitude':ramsey_dt.line_2_amplitude,
                                       'DriftTrackerRamsey.detuning':WithUnit(0,'Hz'),
                                       'StateReadout.use_camera_for_readout':ramsey_dt.use_camera_for_readout,
                                       })
        #replace_1,replace_2 = np.random.permutation([replace_1,replace_2]) this line breaks something
        self.ramsey_dt.set_parameters(replace_1)
        self.ramsey_dt.set_progress_limits(0, 50.0)
        frequency_1,excitation = self.ramsey_dt.run(cxn, context)
        error_sensitivity = ramsey_dt.error_sensitivity
        if not 0.5 - error_sensitivity <= excitation <= 0.5 + error_sensitivity:
            raise Exception("Incorrect Excitation {}".format(replace_1.DriftTrackerRamsey.line_selection)) 
        self.ramsey_dt.set_parameters(replace_2)
        self.ramsey_dt.set_progress_limits(50.0, 100.0)
        frequency_2,excitation = self.ramsey_dt.run(cxn, context)
        if not 0.5 - error_sensitivity <= excitation <= 0.5 + error_sensitivity:
            raise Exception("Incorrect Excitation {}".format(replace_2.DriftTrackerRamsey.line_selection)) 
        self.submit_centers(replace_1,frequency_1,replace_2,frequency_2)
        
        # resetting DDS5 state
        time.sleep(1)
        #self.dds_cw.output('5', False)
        self.dds_cw.output('5', dds5_state)
        time.sleep(1)

    def submit_centers(self, replace_1, center1, replace_2, center2):     
        if center1 is not None and center2 is not None:
            submission = [
                          (replace_1.DriftTrackerRamsey.line_selection, center1),
                          (replace_2.DriftTrackerRamsey.line_selection, center2),
                          ]
            self.drift_tracker.set_measurements(submission)
     
    def finalize(self, cxn, context):
        self.ramsey_dt.finalize(cxn, context)

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = drift_tracker_ramsey(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)