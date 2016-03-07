from common.abstractdevices.script_scanner.scan_methods import experiment
from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from lattice.scripts.PulseSequences.subsequences.StateReadout import state_readout
from lattice.scripts.PulseSequences.subsequences.TurnOffAll import turn_off_all
import numpy as np
from ion_state_detector import ion_state_detector
from labrad.units import WithUnit
from multiprocessing import Process

class ion_auto_load(experiment):
    
    name = 'Ion Auto Load'
    required_parameters = [
                           ('IonsOnCamera','ion_number'),                           
                           ('IonsOnCamera','reference_exposure_factor'),
                           
                           ('IonsOnCamera','vertical_min'),
                           ('IonsOnCamera','vertical_max'),
                           ('IonsOnCamera','vertical_bin'),
                           
                           ('IonsOnCamera','horizontal_min'),
                           ('IonsOnCamera','horizontal_max'),
                           ('IonsOnCamera','horizontal_bin'),
                                                      
                           ('IonsAutoLoad','no_of_detected_ions'),
                           ('IonsAutoLoad','no_of_ions_to_load'),
                           ('IonsAutoLoad','threshold_ion_detection'),
                           ('IonsAutoLoad','repetition_ion_detection'),
                           ('IonsAutoLoad','oven_current'),

                           ('StateReadout','state_readout_duration'),
                           ('StateReadout','repeat_each_measurement'),
                           ('StateReadout','state_readout_amplitude_397'),
                           ('StateReadout','state_readout_frequency_397'),
                           ('StateReadout','state_readout_amplitude_866'),
                           ('StateReadout','state_readout_frequency_866'),
                           ('StateReadout','camera_trigger_width'),
                           ('StateReadout','camera_transfer_additional'),
                           ('StateReadout', 'camera_readout_duration'),
                           
                           ('DopplerCooling','doppler_cooling_repump_additional'),
                           ]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = list(parameters)
        parameters.remove(('StateReadout', 'state_readout_duration'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        p = self.parameters.IonsOnCamera
        #print int(p.ion_number)
        self.fitter = ion_state_detector(int(p.ion_number))
        self.ident = ident
        self.camera = cxn.andor_server
        self.pulser = cxn.pulser
        self.pv = cxn.parametervault

        self.oven_control = cxn.agilent_e3633a

        repetitions = self.parameters.IonsAutoLoad.repetition_ion_detection
        self.pv.set_parameter('StateReadout','repeat_each_measurement', repetitions)

        self.image_region = image_region = [
                             int(p.horizontal_bin),
                             int(p.vertical_bin),
                             int(p.horizontal_min),
                             int(p.horizontal_max),
                             int(p.vertical_min),
                             int(p.vertical_max),
                             ]
        self.camera.abort_acquisition()
        self.initial_exposure = self.camera.get_exposure_time()
        self.parameters.StateReadout.state_readout_duration = self.parameters.StateReadout.camera_readout_duration
        self.camera.set_exposure_time(self.parameters.StateReadout.state_readout_duration)
        self.initial_region = self.camera.get_image_region()
        self.initial_mode = self.camera.get_acquisition_mode()
        self.initial_trigger_mode = self.camera.get_trigger_mode()
        
        
        self.camera.set_acquisition_mode('Kinetics')
        self.camera.set_image_region(*image_region)
        self.camera.set_trigger_mode('External')
        #self.camera.set_trigger_mode
        self.exposures = int(p.reference_exposure_factor) * int(self.parameters.StateReadout.repeat_each_measurement)
        self.camera.set_number_kinetics(self.exposures)
        #generate the pulse sequence
        self.parameters.StateReadout.use_camera_for_readout = True
        start_time = WithUnit(20, 'ms') #do nothing in the beginning to let the camera transfer each image
        self.sequence = pulse_sequence(self.parameters, start = start_time)
        self.sequence.required_subsequences = [state_readout, turn_off_all]
        self.sequence.addSequence(turn_off_all)
        self.sequence.addSequence(state_readout)
        
    def run(self, cxn, context):

        self.camera.start_acquisition()
        self.sequence.programSequence(self.pulser)
        self.pulser.start_number(self.exposures)
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        proceed = self.camera.wait_for_kinetic()
        if not proceed:
            self.camera.abort_acquisition()
            self.finalize(cxn, context)
            raise Exception ("Did not get all kinetic images from camera")
        
        
        images = self.camera.get_acquired_data(self.exposures).asarray

        x_pixels = int( (self.image_region[3] - self.image_region[2] + 1.) / (self.image_region[0]) )
        y_pixels = int(self.image_region[5] - self.image_region[4] + 1.) / (self.image_region[1])
        images = np.reshape(images, (self.exposures, y_pixels, x_pixels))
        image  = np.average(images, axis = 0)
        np.save('37ions_global', image)
        
        self.fit_and_plot(image)

        
    def fit_and_plot(self, image):
        p = self.parameters.IonsOnCamera
        
        threshold = self.parameters.IonsAutoLoad.threshold_ion_detection
        oven_current = self.parameters.IonsAutoLoad.oven_current

        x_axis = np.arange(p.horizontal_min, p.horizontal_max + 1, self.image_region[0])
        y_axis = np.arange(p.vertical_min, p.vertical_max + 1, self.image_region[1])
        xx, yy = np.meshgrid(x_axis, y_axis)


        no_of_detected_ions = self.fitter.integrate_image_vertically(image, threshold)

        print no_of_detected_ions

        self.pv.set_parameter('IonsAutoLoad','no_of_detected_ions', no_of_detected_ions)

        #self.oven_control.select_device(0)
        # too few ions
        if no_of_detected_ions < self.parameters.IonsAutoLoad.no_of_ions_to_load:
            print "Not enough ions ... switching on oven and ionization laser"

            self.pulser.switch_manual('bluePI', True)
            #self.oven_control.current(WithUnit(12.2, 'A'))
            #self.oven_control.output(True)
            #self.oven_control.deselect_device()

            return

        # too many ions
        if no_of_detected_ions > self.parameters.IonsAutoLoad.no_of_ions_to_load:
            print "Need to switch off RF ... too many ions"
            
            #self.pulser.switch_manual('bluePI', False)            
            #self.oven_control.output(False)
            #self.oven_control.deselect_device()

            self.pulser.switch_manual('bluePI', False)
            #self.oven_control.current(WithUnit(12.2, 'A'))
            #self.oven_control.output(True)
            #self.oven_control.deselect_device()

            return

        # the right amount
        self.pulser.switch_manual('bluePI', False)
        #self.oven_control.output(False)
        #self.oven_control.deselect_device()
        return



    def finalize(self, cxn, context):
        self.camera.set_trigger_mode(self.initial_trigger_mode)
        self.camera.set_acquisition_mode(self.initial_mode)
        self.camera.set_exposure_time(self.initial_exposure)
        self.camera.set_image_region(self.initial_region)
        self.camera.start_live_display()

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ion_auto_load(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
