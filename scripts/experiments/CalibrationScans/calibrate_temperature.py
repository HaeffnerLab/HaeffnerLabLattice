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

class calibrate_temperature(experiment):

    name = 'CalibTemperature'

    required_parameters = [('DriftTracker', 'line_selection_1'),
                           ('DriftTracker', 'line_selection_2'),
                           ('CalibrationScans', 'calibrate_sidebands'),
                           ('CalibrationScans', 'feedback_sidebands'),
                           ('CalibrationScans', 'calibration_channel_729'),
                           ('Spectrum','car1_sensitivity'),
                           ('Spectrum','car2_sensitivity')
                           ]

    # parameters to overwrite
    remove_parameters = [
        ('Spectrum','fine'),
        ('Spectrum','ultimate'),
        ('Spectrum','custom'),
        ('Spectrum','manual_amplitude_729'),
        ('Spectrum','manual_excitation_time'),
        ('Spectrum','manual_scan'),
        ('Spectrum','scan_selection'),
        ('Spectrum','sensitivity_selection'),

        ('Display', 'relative_frequencies'),

        ('StateReadout', 'repeat_each_measurement'),
        ('StateReadout', 'use_camera_for_readout'),
        
        ('StatePreparation', 'sideband_cooling_enable'),
        ('StatePreparation', 'optical_pumping_enable'),
        ('Excitation_729', 'bichro'),
        ('Excitation_729', 'channel_729')
        ]

        
        

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(spectrum.all_required_parameters()))
        parameters = list(parameters)
        for p in cls.remove_parameters:
            parameters.remove(p)
        #will be disabling sideband cooling automatically
        parameters.remove(('SidebandCooling','frequency_selection'))
        parameters.remove(('SidebandCooling','manual_frequency_729'))
        parameters.remove(('SidebandCooling','line_selection'))
        parameters.remove(('SidebandCooling','sideband_selection'))
        parameters.remove(('SidebandCooling','sideband_cooling_type'))
        parameters.remove(('SidebandCooling','sideband_cooling_cycles'))
        parameters.remove(('SidebandCooling','sideband_cooling_duration_729_increment_per_cycle'))
        parameters.remove(('SidebandCooling','sideband_cooling_frequency_854'))
        parameters.remove(('SidebandCooling','sideband_cooling_amplitude_854'))
        parameters.remove(('SidebandCooling','sideband_cooling_frequency_866'))

        parameters.remove(('SidebandCooling','sideband_cooling_amplitude_866'))
        parameters.remove(('SidebandCooling','sideband_cooling_amplitude_729'))
        parameters.remove(('SidebandCooling','sideband_cooling_optical_pumping_duration'))
        parameters.remove(('SidebandCoolingContinuous','sideband_cooling_continuous_duration'))
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_729'))
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_cycles'))
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_repumps'))
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_additional_866'))
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_between_pulses'))
        return parameters
    
    
    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.spectrum = self.make_experiment(spectrum)
        
        #self.spectrum.set_parameters(TreeDict.fromdict({'IonsOnCamera.ion_number':1}))
        self.spectrum.initialize(cxn, context, ident,use_camera_override = False)
        #self.spectrum.excite.output_size = 1
        self.fitter = peak_fitter()
        self.pv = cxn.parametervault
        self.dds_cw = cxn.dds_cw

        
    def run(self, cxn, context):
        
        dt = self.parameters.DriftTracker
        
        # save original state of DDS 5
        dds5_state = self.dds_cw.output('5')

        self.dds_cw.output('5', True)
        time.sleep(1)

        sb_red = self.parameters.Spectrum.sideband_selection
        sb_blue = sb_red[:]

        for k in range(len(sb_red)):
            if sb_red[k] > 0.0:
                # in case the sideband selection is set to the blue sideband we need to flip the arrays
                sb_blue[k] = sb_red[k]
                sb_red[k] = -sb_red[k]
            else:
                sb_blue[k] = -sb_red[k]

        #print sb_blue
        #print sb_red

        #no_of_repeats = 50
        relative_frequencies = True

        #### RUN THE RED SIDEBAND

        #'StateReadout.repeat_each_measurement':no_of_repeats,
        replace = TreeDict.fromdict({
            'Spectrum.line_selection':self.parameters.Spectrum.line_selection,
            'Spectrum.scan_selection':'auto',
            'Spectrum.sensitivity_selection': 'normal',
            'Spectrum.sideband_selection':sb_red,
            'SidebandCooling.sideband_selection':sb_red,
            'StatePreparation.sideband_cooling_enable':True,
            'StatePreparation.optical_pumping_enable':True,
            'Display.relative_frequencies':relative_frequencies,
            'StateReadout.use_camera_for_readout':False,
            'Excitation_729.bichro':False,
            'Excitation_729.channel_729':self.parameters.CalibrationScans.calibration_channel_729,
            'StatePreparation.channel_729':self.parameters.CalibrationScans.calibration_channel_729,
            'Spectrum.window_name':['radial1']})

        self.spectrum.set_parameters(self.parameters)
        self.spectrum.set_parameters(replace)
        self.spectrum.set_progress_limits(0.0, 50.0)
        
        fr, ex = self.spectrum.run(cxn, context)

        fr = np.array(fr)
        ex = np.array(ex)
        ex = ex.flatten()

        # take the maximum of the line excitation
        #rsb_ex = np.max(ex)

        try:
            fit_center, rsb_ex, fit_width = self.fitter.fit(fr, ex, return_all_params = True)
        except:
            rsb_ex = np.max(ex)

        #sb_1 = WithUnit(abs(sb_1), 'MHz')

        #### RUN THE BLUE SIDEBAND

        #'StateReadout.repeat_each_measurement':no_of_repeats,
        replace = TreeDict.fromdict({
            'Spectrum.line_selection':self.parameters.Spectrum.line_selection,
            'Spectrum.scan_selection':'auto',
            'Spectrum.sensitivity_selection': 'normal',
            'Spectrum.sideband_selection':sb_blue,
            'SidebandCooling.sideband_selection':sb_red,
            'StatePreparation.sideband_cooling_enable':True,
            'StatePreparation.optical_pumping_enable':True,
            'Display.relative_frequencies':relative_frequencies,
            'StateReadout.use_camera_for_readout':False,
            'Excitation_729.bichro':False,
            'Excitation_729.channel_729':self.parameters.CalibrationScans.calibration_channel_729,
            'StatePreparation.channel_729':self.parameters.CalibrationScans.calibration_channel_729,
            'Spectrum.window_name':['radial2']})

        self.spectrum.set_parameters(self.parameters)
        self.spectrum.set_parameters(replace)
        self.spectrum.set_progress_limits(50.0, 100.0)
        
        fr, ex = self.spectrum.run(cxn, context)

        fr = np.array(fr)
        ex = np.array(ex)
        ex = ex.flatten()

        # take the maximum of the line excitation
        #bsb_ex = np.max(ex)

        try:
            fit_center, bsb_ex, fit_width = self.fitter.fit(fr, ex, return_all_params = True)
        except:
            bsb_ex = np.max(ex)

        #sb_2 = WithUnit(abs(sb_2), 'MHz')
             
        # resetting DDS5 state
        time.sleep(1)
        #self.dds_cw.output('5', False)
        self.dds_cw.output('5', dds5_state)
        time.sleep(1)

        return (rsb_ex, bsb_ex)

    def finalize(self, cxn, context):
        self.spectrum.finalize(cxn, context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = calibrate_temperature(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
