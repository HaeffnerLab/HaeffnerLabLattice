from common.abstractdevices.script_scanner.scan_methods import experiment
import numpy as np
from ion_fitting import linear_chain_fitter

class reference_camera_image(experiment):
    
    name = 'Reference Camera Image'
    required_parameters = [
                           ('IonsOnCamera','ion_number'),
                           ('IonsOnCamera','vertical_min'),
                           ('IonsOnCamera','vertical_max'),
                           ('IonsOnCamera','horizontal_min'),
                           ('IonsOnCamera','horizontal_max'),
                           ('StateReadout','state_readout_duration'),
                           ('StateReadout','repeat_each_measurement'),
                           ]
    

    def initialize(self, cxn, context, ident):
        self.fitter = linear_chain_fitter()
        self.ident = ident
        self.camera = cxn.andor_server
        self.pv = cxn.parametervault
        p = self.parameters.IonsOnCamera
        self.image_region = image_region = [
                             1,#bin_x
                             1,#bin_y
                             int(p.horizontal_min),
                             int(p.horizontal_max),
                             int(p.vertical_min),
                             int(p.vertical_max),
                             ]
        self.camera.abort_acquisition()
        self.initial_exposure = self.camera.get_exposure_time()
        self.camera.set_exposure_time(self.parameters.StateReadout.state_readout_duration)
        self.initial_region = self.camera.get_image_region()
        self.camera.set_image_region(*image_region)
        self.camera.set_acquisition_mode('Kinetics')
        self.camera.set_number_kinetics(int(self.parameters.StateReadout.repeat_each_measurement))

    def run(self, cxn, context):
        repetitions = int(self.parameters.StateReadout.repeat_each_measurement) 
        self.camera.start_acquisition()
        proceed = self.camera.wait_for_kinetic()
        while not proceed:
            print 'still waiting for kinetics'
            proceed = self.camera.wait_for_kinetic()
        images = self.camera.get_acquired_data(repetitions).asarray
        x_pixels = self.image_region[3] - self.image_region[2] + 1
        y_pixels = self.image_region[5] - self.image_region[4] + 1
        images = np.reshape(images, (repetitions, y_pixels, x_pixels))
        image  = np.average(images, axis = 0)
        self.fit_and_plot(image)
        
    def fit_and_plot(self, image):
        p = self.parameters.IonsOnCamera
        x_axis = np.arange(p.horizontal_min, p.horizontal_max + 1)
        y_axis = np.arange(p.vertical_min, p.vertical_max + 1)
        xx, yy = np.meshgrid(x_axis, y_axis)
        result, params = self.fitter.guess_parameters_and_fit(xx, yy, image, p.ion_number)
        self.fitter.report(params)
        from multiprocessing import Process
        p = Process(target = self.fitter.graph, args = (x_axis, y_axis, image, params, result))
        #self.fitter.graph(x_axis, y_axis, image, result)
        p.start()
        self.pv.set_parameter('IonsOnCamera','fit_background_level', params['background_level'].value)
        self.pv.set_parameter('IonsOnCamera','fit_amplitude', params['amplitude'].value)
        self.pv.set_parameter('IonsOnCamera','fit_rotation_angle', params['rotation_angle'].value)
        self.pv.set_parameter('IonsOnCamera','fit_center_horizontal', params['center_x'].value)
        self.pv.set_parameter('IonsOnCamera','fit_center_vertical', params['center_y'].value)
        self.pv.set_parameter('IonsOnCamera','fit_spacing', params['spacing'].value)
        self.pv.set_parameter('IonsOnCamera','fit_sigma', params['sigma'].value)

    def finalize(self, cxn, context):
        self.camera.set_exposure_time(self.initial_exposure)
        self.camera.set_image_region(self.initial_region)
        self.camera.start_live_display()

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = reference_camera_image(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)