from common.abstractdevices.script_scanner.scan_methods import experiment
from spectrum import spectrum

class drift_tracker(experiment):
    
    name = 'DriftTracker'
    required_parameters = [
                           ('DriftTracker','line_selection_1'),
                           ('DriftTracker','line_selection_2'),
                           ('DriftTracker','sensitivity_selection_1'),
                           ('DriftTracker','sensitivity_selection_2'),
                           ]
    
    required_parameters.extend(spectrum.required_parameters)
    #removing parameters we'll be overwriting, and they do not need to be loaded
    required_parameters.remove(('Spectrum','line_selection'))
    required_parameters.remove(('Spectrum','manual_amplitude_729'))
    required_parameters.remove(('Spectrum','manual_excitation_time'))
    required_parameters.remove(('Spectrum','manual_scan'))
    required_parameters.remove(('Spectrum','scan_selection'))
    required_parameters.remove(('Spectrum','sensitivity_selection'))
    required_parameters.remove(('Spectrum','sideband_selection'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.spectrum = self.make_experiment(spectrum)
        self.spectrum.initialize(cxn, context, ident)
        self.parameters['Spectrum.scan_selection'] = 'auto'
        self.parameters['Spectrum.sideband_selection'] = [0,0,0,0]
        
    def run(self, cxn, context):
        dt = self.parameters.DriftTracker
        if dt.line_selection_1 == dt.line_selection_2:
            raise Exception ("The two Drift Tracking lines can not be the same")
        self.parameters['Spectrum.line_selection'] = dt.line_selection_1
        self.parameters['Spectrum.sensitivity_selection'] = dt.sensitivity_selection_1
        self.parameters['Spectrum.window_name'] = ['Drift Tracker {0}'.format(dt.line_selection_1)]
        self.spectrum.set_parameters(self.parameters)
        self.spectrum.set_progress_limits(0, 50.0)
        self.spectrum.run(cxn, context)
        if self.spectrum.should_stop: return
        self.parameters['Spectrum.line_selection'] = dt.line_selection_2
        self.parameters['Spectrum.sensitivity_selection'] = dt.sensitivity_selection_2
        self.parameters['Spectrum.window_name'] = ['Drift Tracker {0}'.format(dt.line_selection_2)]
        self.spectrum.set_parameters(self.parameters)
        self.spectrum.set_progress_limits(50.0, 100.0)
        self.spectrum.run(cxn, context)
        if self.spectrum.should_stop: return
     
    def finalize(self, cxn, context):
        self.spectrum.finalize(cxn, context)

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = drift_tracker(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)