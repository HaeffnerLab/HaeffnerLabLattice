from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np
from Camera.ion_state_detector import ion_state_detector
from multiprocessing import Process


class ReferenceImage(pulse_sequence):
    scannable_params = {
        'temp':  [(0., 1., 1, 'us'), 'current']}
    
    show_params= ['IonsOnCamera.ion_number',
                  'IonsOnCamera.reference_exposure_factor',
                  'IonsOnCamera.vertical_min',
                  'IonsOnCamera.vertical_max',
                  'IonsOnCamera.vertical_bin',
                  'IonsOnCamera.horizontal_min',
                  'IonsOnCamera.horizontal_max',
                  'IonsOnCamera.horizontal_bin',
                  'StateReadout.state_readout_duration',
                  'StateReadout.repeat_each_measurement',
                  'StateReadout.state_readout_amplitude_397',
                  'StateReadout.state_readout_frequency_397',
                  'StateReadout.state_readout_amplitude_866',
                  'StateReadout.state_readout_frequency_866',
                  'StateReadout.camera_trigger_width',
                  'StateReadout.camera_transfer_additional',
                  'StateReadout.camera_readout_duration',
                  'DopplerCooling.doppler_cooling_repump_additional'
                  ]
    
    fixed_params = {'StateReadout.readout_mode':'camera'}



    def sequence(self):
        from subsequences.RepumpD import RepumpD
        from subsequences.DopplerCooling import DopplerCooling
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        
        # building the sequence
        self.end = U(20, 'ms') #do nothing in the beginning to let the camera transfer each image
        self.addSequence(TurnOffAll)  
        self.addSequence(RepumpD) # initializing the state of the ion
        self.addSequence(DopplerCooling)  
        self.addSequence(StateReadout,{"StateReadout.use_camera_for_readout": True})
        
   
                
        
    @classmethod
    def run_initial(cls, cxn, parameters_dict):
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_in_loop(cls, cxn, parameters_dict, data_so_far,x):
        pass
    @classmethod
    def run_finally(cls, cxn, parameters_dict, images,x):
        #import matplotlib.pyplot as plt
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)
        
        print "RUNNING Reference image analysis"
        pv = cxn.scriptscanner
        
        p = parameters_dict.IonsOnCamera
        image_region = [
                             int(p.horizontal_bin),
                             int(p.vertical_bin),
                             int(p.horizontal_min),
                             int(p.horizontal_max),
                             int(p.vertical_min),
                             int(p.vertical_max),
                             ]
        
        # temporary image
        x_pixels = int( (image_region[3] - image_region[2] + 1.) / (image_region[0]) )
        y_pixels = int(image_region[5] - image_region[4] + 1.) / (image_region[1])
        
        repetitions=parameters_dict.StateReadout.repeat_each_measurement
        images = np.reshape(images, (repetitions, y_pixels, x_pixels))
        
        image  = np.average(images, axis = 0)
        np.save('temp_camera2.npy',image)
        np.save('temp_camera3.npy',images)
        
        
        #plt.imshow(image)
        #plt.show()
        
        
        x_axis = np.arange(p.horizontal_min, p.horizontal_max + 1, image_region[0])
        y_axis = np.arange(p.vertical_min, p.vertical_max + 1, image_region[1])
        xx, yy = np.meshgrid(x_axis, y_axis)
               
        fitter = ion_state_detector(int(p.ion_number))
        result, params = fitter.guess_parameters_and_fit(xx, yy, image)
        fitter.report(params)
        #ideally graphing should be done by saving to data vault and using the grapher
        #fitter.graph(x_axis, y_axis, image, params, result)
        #p = Process(target = fitter.graph, args = (x_axis, y_axis, image, params, result))
        #p.start()
        fitter.graph(x_axis, y_axis, image, params, result)
        pv.set_parameter('IonsOnCamera','fit_background_level', params['background_level'].value)
        pv.set_parameter('IonsOnCamera','fit_amplitude', params['amplitude'].value)
        pv.set_parameter('IonsOnCamera','fit_rotation_angle', params['rotation_angle'].value)
        pv.set_parameter('IonsOnCamera','fit_center_horizontal', params['center_x'].value)
        pv.set_parameter('IonsOnCamera','fit_center_vertical', params['center_y'].value)
        pv.set_parameter('IonsOnCamera','fit_spacing', params['spacing'].value)
        pv.set_parameter('IonsOnCamera','fit_sigma', params['sigma'].value)
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    sc = cxn.scriptscanner
    scan = [('ReferenceImage',   ('temp', 0, 1, 1, 'us'))]
    ident = sc.new_sequence('ReferenceImage', scan)
    sc.sequence_completed(ident)
    cxn.disconnect()
        
        
        
        
        
        

        

