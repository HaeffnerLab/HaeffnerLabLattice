from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.PulseSequences.spectrum_rabi import spectrum_rabi
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
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
                           ]
    required_parameters.extend(spectrum_rabi.required_parameters)
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
        print 'cooling at freq', sideband_cooling_frequency
        self.parameters['SidebandCooling.sideband_cooling_frequency_729'] = sideband_cooling_frequency
    
    def setup_initial_switches(self):
        self.pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
        self.pulser.switch_manual('crystallization',  False)
        #switch off 729 at the beginning
        self.pulser.output('729DP', False)
        
    def run(self, cxn, context):
        threshold = int(self.parameters.StateReadout.state_readout_threshold)
        repetitions = int(self.parameters.StateReadout.repeat_each_measurement)
        pulse_sequence = spectrum_rabi(self.parameters)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_number(repetitions)
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        readouts = self.pulser.get_readout_counts().asarray
        perc_excited = numpy.count_nonzero(readouts <= threshold) / float(len(readouts))
        self.save_data(readouts)
        return perc_excited
    
    def finalize(self, cxn, context):
        pass
              
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