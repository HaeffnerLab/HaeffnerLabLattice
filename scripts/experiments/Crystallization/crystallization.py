from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Camera.ion_state_detector import ion_state_detector
from labrad.units import WithUnit
import numpy as np

class crystallization(experiment):
    
    name = 'crystallization'  
    crystallization_required_parameters = [
                            ('Crystallization','camera_threshold'),
                            ('Crystallization','max_attempts'),
                            ('Crystallization','max_duration'),
                            ('Crystallization','min_duration'),
                            ('Crystallization','pmt_threshold'),
                            ('Crystallization','pmt_record_duration'),
                            ('Crystallization','use_camera'),
                            ('Crystallization','camera_record_exposure'),
                           
                            ('IonsOnCamera','ion_number'),
                            ('IonsOnCamera','vertical_min'),
                            ('IonsOnCamera','vertical_max'),
                            ('IonsOnCamera','vertical_bin'),
                            ('IonsOnCamera','horizontal_min'),
                            ('IonsOnCamera','horizontal_max'),
                            ('IonsOnCamera','horizontal_bin'),
                           
                            ('IonsOnCamera','fit_amplitude'),
                            ('IonsOnCamera','fit_background_level'),
                            ('IonsOnCamera','fit_center_horizontal'),
                            ('IonsOnCamera','fit_center_vertical'),
                            ('IonsOnCamera','fit_rotation_angle'),
                            ('IonsOnCamera','fit_sigma'),
                            ('IonsOnCamera','fit_spacing'),
                           ]
    
    @classmethod
    def all_required_parameters(cls):
        return cls.crystallization_required_parameters
    
    def initialize(self, cxn, context, ident):
        p = self.parameters.Crystallization
        self.crystallizer = cxn.crystallizer
        if p.use_camera:
            self.camera = cxn.andor_server
            self.threshold = p.camera_threshold
            self.get_ion_signal = self.get_camera_counts 
            self.initialize_camera()
        else:
            self.flow = cxn.normalpmtflow
            self.threshold = p.pmt_threshold
            self.get_ion_signal = self.get_pmt_counts
        print 'getting camera counts'
        self.initial_signal = self.get_ion_signal()
    
    def get_camera_counts(self):
        exposure = self.parameters.Crystallization.camera_record_exposure
        initial_exposure = self.camera.get_exposure_time()
        initial_acquisition_mode = self.camera.get_acquisition_mode()
        initial_live_display = self.camera.is_live_display_running()
        initial_trigger_mode = self.camera.get_trigger_mode()
        self.camera.abort_acquisition()
        self.camera.set_exposure_time(exposure)
        self.camera.set_acquisition_mode('Single Scan')
        self.camera.set_trigger_mode('Internal')
        self.camera.start_acquisition()
        self.camera.wait_for_acquisition()
        image = self.camera.get_acquired_data().asarray
        x_pixels = int(self.image_region[3] - self.image_region[2] + 1.) / (self.image_region[0])
        y_pixels = int(self.image_region[5] - self.image_region[4] + 1.) / (self.image_region[1])
        image = np.reshape(image, (1, y_pixels, x_pixels))
        self.camera.abort_acquisition()
        self.camera.set_exposure_time(initial_exposure)
        self.camera.set_acquisition_mode(initial_acquisition_mode)
        self.camera.set_trigger_mode(initial_trigger_mode)
        if initial_live_display:
            self.camera.start_live_display()
        #process the image
        counts = self.fitter.get_total_counts(image)[0]
        print counts
        return counts
    
    def get_pmt_counts(self):
        p = self.parameters.Crystallization
        counts = p.pmt_record_duration / self.flow.get_time_length()
        counts = int(counts.value)
        ion_signal = self.flow.get_next_counts('ON', counts, True)
        return ion_signal
    
    def initialize_camera(self):
        p = self.parameters.IonsOnCamera
        from lmfit import Parameters as lmfit_Parameters
        self.fitter = ion_state_detector(int(p.ion_number))
        self.image_region = [
                             int(p.horizontal_bin),
                             int(p.vertical_bin),
                             int(p.horizontal_min),
                             int(p.horizontal_max),
                             int(p.vertical_min),
                             int(p.vertical_max),
                             ]
        
        self.fit_parameters = lmfit_Parameters()
        self.fit_parameters.add('ion_number', value = int(p.ion_number))
        self.fit_parameters.add('background_level', value = p.fit_background_level)
        self.fit_parameters.add('amplitude', value = p.fit_amplitude)
        self.fit_parameters.add('rotation_angle', p.fit_rotation_angle)
        self.fit_parameters.add('center_x', value = p.fit_center_horizontal)
        self.fit_parameters.add('center_y', value = p.fit_center_vertical)
        self.fit_parameters.add('spacing', value = p.fit_spacing)
        self.fit_parameters.add('sigma', value = p.fit_sigma)
        x_axis = np.arange(self.image_region[2], self.image_region[3] + 1, self.image_region[0])
        y_axis = np.arange(self.image_region[4], self.image_region[5] + 1, self.image_region[1])
        xx,yy = np.meshgrid(x_axis, y_axis)
        self.fitter.set_fitted_parameters(self.fit_parameters, xx, yy)

    def run(self, cxn, context):
        '''
        run the crystallization procedure:
        
        returns [was_melted, crystallization successful]
        
        '''
        initially_melted = False
        p = self.parameters.Crystallization
        attempts = int(p.max_attempts)
        durations = np.linspace(p.min_duration['s'], p.max_duration['s'], attempts)
        for duration in durations:
            counts = self.get_ion_signal()
            if counts >= self.threshold * self.initial_signal:
                return [initially_melted, True]
            else:
                initially_melted = True
            self.crystallizer.crystallize_once(WithUnit(duration,'s'))
        return [initially_melted, False]
    
    def finalize(self, cxn, context):
        pass
    
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = crystallization(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)