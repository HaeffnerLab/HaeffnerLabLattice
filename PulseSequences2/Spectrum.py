#!scriptscanner

from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict

class Spectrum(pulse_sequence):
    
    
                            #(self, scan_param, minim, maxim, steps, unit)
    scannable_params = {
        #'Spectrum.carrier_detuning':  [(-50, 50, 100, 'kHz'), 'window']
        'Spectrum.carrier_detuning' : [(-150, 150, 10, 'kHz'),'spectrum'],
        'Spectrum.sideband_detuning' :[(-50, 50, 100, 'kHz'),'spectrum']
              }

    show_params= ['Excitation_729.channel_729',
                  'Excitation_729.bichro',
                  'Spectrum.manual_amplitude_729',
                  'Spectrum.manual_excitation_time',
                  'Spectrum.line_selection',
                  'Spectrum.selection_sideband',
                  'Spectrum.order',
                  'Display.relative_frequencies',
                  'StatePreparation.channel_729',
                  'StatePreparation.optical_pumping_enable',
                  'StatePreparation.sideband_cooling_enable'
                  ]
   
    #fixed_params = {'StateReadout.ReadoutMode':'camera'}
    
    def sequence(self):
        
        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
           
        ## calculate the scan params
        spc = self.parameters.Spectrum   
        
        if spc.selection_sideband == "off":         
            freq_729=self.calc_freq(spc.line_selection)
        else:
            freq_729=self.calc_freq(spc.line_selection, spc.selection_sideband ,int(spc.order))
        
        freq_729=freq_729 + spc.carrier_detuning + spc.sideband_detuning
        
        amp=spc.manual_amplitude_729
        duration=spc.manual_excitation_time
        print "Spectrum scan"
        print "729 freq: {}".format(freq_729.inUnitsOf('MHz'))
        print "729 detuning: {}".format(freq_729-self.calc_freq(spc.line_selection))
        print "729 amp is {}".format(amp)
        print "729 duration is {}".format(duration)
        
        

                
        # building the sequence
        # needs a 10 micro sec for some reason
        self.end = U(10., 'us')
        self.addSequence(TurnOffAll)           
        self.addSequence(StatePreparation)      
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration':  duration })
        self.addSequence(StateReadout)
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    sc = cxn.scriptscanner
    #scan = [('ReferenceImage',   ('temp', 0, 1, 1, 'us'))]
    scan =[('Spectrum',   ('Spectrum.carrier_detuning', -150, 150, 10, 'kHz'))] 
    ident = sc.new_sequence('Spectrum', scan)
    sc.sequence_completed(ident)
    cxn.disconnect()