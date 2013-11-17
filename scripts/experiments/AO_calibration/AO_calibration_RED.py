from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.scriptLibrary.fly_processing import Binner
from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter
import time
from numpy import linspace
from labrad.units import WithUnit
import labrad
import numpy
       
class AO_calibration_Red(experiment):
    
    name = 'AO_calibration_Red'
    
    required_parameters = [
                           ('AO_calibration','target_power'),
                           ('AO_calibration','point_per_frequency'),
                           ('AO_calibration','delay_time'),
                           ('BareLineScan','frequency_scan'),
                           ]
    
    #required_parameters.extend(sequence.required_parameters)
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = cxn.data_vault
        self.power_meter = cxn.power_meter_server
        self.pulser = cxn.pulser
        self.light_power_v_frequency_save_context = cxn.context()
        self.calibrated_power_save_context = cxn.context()
        self.scan = []
        self.scan_no_unit = []
        self.delay_time = self.parameters.AO_calibration.delay_time['s']
        self.points_per_frequency = int(self.parameters.AO_calibration.point_per_frequency)
        
    def setup_sequence_parameters(self):
        line_scan = self.parameters.BareLineScan
        minim,maxim,steps = line_scan.frequency_scan
        minim = minim['MHz']; maxim = maxim['MHz']
        self.scan_no_unit = linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'MHz') for pt in self.scan_no_unit]
    
    #def setup_data_vault(self):
        
            
    def get_calibrated_frequency_scan(self,calibrated_power,step):
        self.power_meter.select_device(0)
        self.power_meter.set_wavelength(866)
        target_power = self.parameters.AO_calibration.target_power['W']
        for i,frequency_866 in enumerate(self.scan):
            amplitude = calibrated_power[i]
            self.pulser.amplitude('866DP', WithUnit(amplitude, 'dBm'))
            print amplitude
            self.pulser.frequency('866DP', frequency_866)
            time.sleep(self.delay_time)
            measured_power = []
            for j in range(self.points_per_frequency):
                power = self.power_meter.measure()
                time.sleep(self.delay_time)
                measured_power.extend(numpy.array([power['W']]))
            averaged_power = numpy.average(measured_power)
            while (averaged_power-target_power>0.0):
                amplitude = amplitude - step
                self.pulser.amplitude('866DP', WithUnit(amplitude, 'dBm'))        
                print amplitude               
                measured_power = []           
                for j in range(self.points_per_frequency):
                    power = self.power_meter.measure()
                    time.sleep(self.delay_time)
                    measured_power.extend(numpy.array([power['W']]))
                    averaged_power = numpy.average(measured_power)                       
            calibrated_power[i]=amplitude+step    
        return calibrated_power
    
    def calibrated_scan(self,calibrated_power):
        #cxn.pulser.frequency('global397')
        self.power_meter.select_device(0)
        self.power_meter.set_wavelength(866)
        
        self.dv.cd(['','QuickMeasurements'],True, context=self.light_power_v_frequency_save_context)
        self.dv.new('AO freq response',[('Frequency', 'MHz')], [('Light Power', 'Power','mW')], context=self.light_power_v_frequency_save_context)
        self.dv.add_parameter('plotLive',True, context=self.light_power_v_frequency_save_context)
        self.dv.add_parameter('Window', ['AO freq response'], context = self.light_power_v_frequency_save_context)    
        
        power_array = []
        
        for i,frequency_866 in enumerate(self.scan):
            self.pulser.frequency('866DP', frequency_866)
            print i,frequency_866
            self.pulser.amplitude('866DP',WithUnit(calibrated_power[i],'dBm'))
            print calibrated_power[i]
            measured_power = []
            for j in range(self.points_per_frequency):
                time.sleep(self.delay_time)
                power = self.power_meter.measure()
                measured_power.extend(numpy.array([power['W']]))
                #print j
            averaged_power = numpy.average(measured_power)
            power_array.extend(numpy.array([averaged_power]))
            frequency_866_no_unit = frequency_866['MHz']
            #print frequency_397
            self.dv.add([frequency_866_no_unit,averaged_power],context=self.light_power_v_frequency_save_context) 
            

    def run(self, cxn, context):
        self.setup_sequence_parameters()
        calibrated_power = numpy.ones_like(self.scan_no_unit)*(-12.0)
        self.dv.cd(['','QuickMeasurements'],True, context=self.calibrated_power_save_context)
        self.dv.new('Calibrated Power',[('Frequency', 'MHz')], [('AO Power', 'Power','dBm')], context=self.calibrated_power_save_context)
        self.dv.add_parameter('plotLive',True, context=self.calibrated_power_save_context)
        self.dv.add_parameter('Window', ['Calibrated Power'], context=self.calibrated_power_save_context)
        
        for i in range(7):
            should_stop = self.pause_or_stop()
            if should_stop: break
            calibrated_power = self.get_calibrated_frequency_scan(calibrated_power,2.0/(2.0**i))
            print calibrated_power
            self.calibrated_scan(calibrated_power)
            self.update_progress(i)
            
        self.dv.add(numpy.vstack((self.scan_no_unit,calibrated_power)).transpose(),context=self.calibrated_power_save_context)
    
    def finalize(self, cxn, context):
        self.save_parameters(self.dv, cxn, self.cxnlab, self.calibrated_power_save_context)
    
    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / 7.0
        self.sc.script_set_progress(self.ident,  progress)
        
    def save_parameters(self, dv, cxn, cxnlab, context):
        measuredDict = dvParameters.measureParameters(cxn, cxnlab)
        dvParameters.saveParameters(dv, measuredDict, context)
        dvParameters.saveParameters(dv, dict(self.parameters), context)          

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = AO_calibration_Red(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)