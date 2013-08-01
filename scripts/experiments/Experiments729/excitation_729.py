from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.PulseSequences.spectrum_rabi import spectrum_rabi
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.experiments.Camera.ion_fitting import linear_chain_fitter
import numpy
import time
       
class excitation_729(experiment):
    
    name = 'Excitation729'  
    required_parameters = [('OpticalPumping','frequency_selection'),
                           ('OpticalPumping','manual_frequency_729'),
                           ('OpticalPumping','line_selection'),
                           
                           ('SidebandCooling','frequency_selection'),
                           ('SidebandCooling','manual_frequency_729'),
                           ('SidebandCooling','line_selection'),
                           ('SidebandCooling','sideband_selection'),
                           ('TrapFrequencies','axial_frequency'),
                           ('TrapFrequencies','radial_frequency_1'),
                           ('TrapFrequencies','radial_frequency_2'),
                           ('TrapFrequencies','rf_drive_frequency'),
                           
                           ('StateReadout', 'repeat_each_measurement'),
                           ('StateReadout', 'state_readout_threshold'),
                           ('StateReadout', 'use_camera_for_readout'),
                           ('StateReadout', 'state_readout_duration'),
                           
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
    pulse_sequence = spectrum_rabi
    required_parameters.extend(pulse_sequence.required_parameters)
    #removing pulse sequence items that will be calculated in the experiment and do not need to be loaded
    required_parameters.remove(('OpticalPumping', 'optical_pumping_frequency_729'))
    required_parameters.remove(('SidebandCooling', 'sideband_cooling_frequency_729'))
    
    def initialize(self, cxn, context, ident):
        self.pulser = cxn.pulser
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.total_readouts = []
        self.readout_save_context = cxn.context()
        self.histogram_save_context = cxn.context()
        self.readout_save_iteration = 0
        self.setup_sequence_parameters()
        self.setup_initial_switches()
        self.setup_data_vault()
        self.use_camera = self.parameters.StateReadout.use_camera_for_readout
        if self.use_camera:
            self.initialize_camera(cxn)
            
    def initialize_camera(self, cxn):
        import lmfit
        self.camera = cxn.andor_server
        self.fitter = linear_chain_fitter()
        self.camera_initially_live_display = self.camera.is_live_display_running()
        self.camera.abort_acquisition()
        self.initial_exposure = self.camera.get_exposure_time()
        exposure = self.parameters.StateReadout.state_readout_duration
        self.camera.set_exposure_time(exposure)
        self.initial_region = self.camera.get_image_region()
        p = self.parameters.IonsOnCamera
        self.image_region = [
                             int(p.horizontal_bin),
                             int(p.vertical_bin),
                             int(p.horizontal_min),
                             int(p.horizontal_max),
                             int(p.vertical_min),
                             int(p.vertical_max),
                             ]
        
        self.fit_parameters = lmfit.Parameters()
        self.fit_parameters.add('ion_number', value = int(p.ion_number))
        self.fit_parameters.add('background_level', value = p.fit_background_level)
        self.fit_parameters.add('amplitude', value = p.fit_amplitude)
        self.fit_parameters.add('rotation_angle', p.fit_rotation_angle)
        self.fit_parameters.add('center_x', value = p.fit_center_horizontal)
        self.fit_parameters.add('center_y', value = p.fit_center_vertical)
        self.fit_parameters.add('spacing', value = p.fit_spacing)
        self.fit_parameters.add('sigma', value = p.fit_sigma)
        self.camera.set_image_region(*self.image_region)
        self.camera.set_acquisition_mode('Kinetics')
        self.initial_trigger_mode = self.camera.get_trigger_mode()
        self.camera.set_trigger_mode('External')
        self.camera.set_number_kinetics(int(self.parameters.StateReadout.repeat_each_measurement))

    def setup_data_vault(self):
        localtime = time.localtime()
        self.datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        self.save_directory = ['','Experiments']
        self.save_directory.extend([self.name])
        self.save_directory.extend(dirappend)
        self.dv.cd(self.save_directory ,True, context = self.readout_save_context)
        self.dv.new('Readout {}'.format(self.datasetNameAppend),[('Iteration', 'Arb')],[('Readout Counts','Arb','Arb')], context = self.readout_save_context)        
    
    def setup_sequence_parameters(self):
        op = self.parameters.OpticalPumping
        optical_pumping_frequency = cm.frequency_from_line_selection(op.frequency_selection, op.manual_frequency_729, op.line_selection, self.drift_tracker)
        self.parameters['OpticalPumping.optical_pumping_frequency_729'] = optical_pumping_frequency
        sc = self.parameters.SidebandCooling
        sideband_cooling_frequency = cm.frequency_from_line_selection(sc.frequency_selection, sc.manual_frequency_729, sc.line_selection, self.drift_tracker)
        if sc.frequency_selection == 'auto': 
            trap = self.parameters.TrapFrequencies
            sideband_cooling_frequency = cm.add_sidebands(sideband_cooling_frequency, sc.sideband_selection, trap)
        self.parameters['SidebandCooling.sideband_cooling_frequency_729'] = sideband_cooling_frequency
    
    def setup_initial_switches(self):
        self.pulser.switch_manual('crystallization',  False)
        #switch off 729 at the beginning
        self.pulser.output('729DP', False)
        
    def run(self, cxn, context):
        threshold = int(self.parameters.StateReadout.state_readout_threshold)
        repetitions = int(self.parameters.StateReadout.repeat_each_measurement)
        pulse_sequence = self.pulse_sequence(self.parameters)
        pulse_sequence.programSequence(self.pulser)
        #to plot the excitation as it happens
#         from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter
#         dds = cxn.pulser.human_readable_dds()
#         ttl = cxn.pulser.human_readable_ttl()
#         channels = cxn.pulser.get_channels().asarray
#         sp = SequencePlotter(ttl.asarray, dds.aslist, channels)
#         sp.makePlot()
        if self.use_camera:
            #print 'starting acquisition'
            self.camera.start_acquisition()
        self.pulser.start_number(repetitions)
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        readouts = self.pulser.get_readout_counts().asarray
        self.save_data(readouts)
        if not self.use_camera:
            #get percentage of the excitation using the PMT threshold
            if len(readouts):
                perc_excited = numpy.count_nonzero(readouts <= threshold) / float(len(readouts))
            else:
                #got no readouts
                perc_excited = -1.0
            perc_excited = [perc_excited]
#             print readouts
        else:
            #get the percentage of excitation using the camera state readout
            proceed = self.camera.wait_for_kinetic()
            if not proceed:
                self.camera.abort_acquisition()
                self.finalize(cxn, context)
                raise Exception ("Did not get all kinetic images from camera")
            images = self.camera.get_acquired_data(repetitions).asarray
            self.camera.abort_acquisition()
            x_pixels = int( (self.image_region[3] - self.image_region[2] + 1.) / (self.image_region[0]) )
            y_pixels = int(self.image_region[5] - self.image_region[4] + 1.) / (self.image_region[1])
            images = numpy.reshape(images, (repetitions, y_pixels, x_pixels))
            ion_number = int(self.parameters.IonsOnCamera.ion_number)
            bright_ions = numpy.empty((repetitions, ion_number))
            all_differences = []
            x_axis = numpy.arange(self.image_region[2], self.image_region[3] + 1, self.image_region[0])
            y_axis = numpy.arange(self.image_region[4], self.image_region[5] + 1, self.image_region[1])
            xx,yy = numpy.meshgrid(x_axis, y_axis)
            #useful for debugging, saving the images
            #numpy.save('readout', images)
            for current, image in enumerate(images):
                current_bright, current_differences = self.fitter.state_detection(xx, yy, image, self.fit_parameters)
                #debugging by plotting the image along with its chi squared difference
                #print current_bright, current_differences
                #from matplotlib import pyplot
                #pyplot.figure()
                #pyplot.contourf(image, vmin = 500, vmax = 750)
                #pyplot.show()
                all_differences.extend(current_differences)
                bright_ions[current] = current_bright
            all_differences = numpy.array(all_differences)
            perc_excited = 1 - numpy.average(bright_ions, axis = 0)
            #useful for debugging to print PMT readout vs Camera readout
            #print 'PMT', numpy.count_nonzero(readouts <= threshold) / float(len(readouts)), 'CAMERA', perc_excited
        return perc_excited
    
    @property
    def output_size(self):
        if self.use_camera:
            return int(self.parameters.IonsOnCamera.ion_number)
        else:
            return 1
    
    def finalize(self, cxn, context):
        if self.use_camera:
            #if used the camera, return it to the original settings
            self.camera.set_trigger_mode(self.initial_trigger_mode)
            self.camera.set_exposure_time(self.initial_exposure)
            self.camera.set_image_region(self.initial_region)
            if self.camera_initially_live_display:
                self.camera.start_live_display()
               
    def save_data(self, readouts):
        #save the current readouts
        iters = numpy.ones_like(readouts) * self.readout_save_iteration
        self.dv.add(numpy.vstack((iters, readouts)).transpose(), context = self.readout_save_context)
        self.readout_save_iteration += 1
        self.total_readouts.extend(readouts)
        if (len(self.total_readouts) >= 500):
            hist, bins = numpy.histogram(self.total_readouts, 50)
            self.dv.cd(self.save_directory ,True, context = self.histogram_save_context)
            self.dv.new('Histogram {}'.format(self.datasetNameAppend),[('Counts', 'Arb')],[('Occurence','Arb','Arb')], context = self.histogram_save_context )
            self.dv.add(numpy.vstack((bins[0:-1],hist)).transpose(), context = self.histogram_save_context )
            self.dv.add_parameter('Histogram729', True, context = self.histogram_save_context )
            self.total_readouts = []

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = excitation_729(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)