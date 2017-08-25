# heating rate measurement

import labrad
cxn = labrad.connect()
sc = cxn.scriptscanner

# make this function
ident1 = sc.new_sequence_with_replace('Spectrum', [('Spectrum.sideband_detuning', -20, 20, 40, 'kHz')], 
                             [('Spectrum.order',1)])

 #[('Spectrum.sideband_detuning', -20, 20, 40, 'kHz'), ('Spectrum.sideband_detuning', -20, 20, 40, 'kHz')]