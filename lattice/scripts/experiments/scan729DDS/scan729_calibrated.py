import labrad
import numpy
from fly_processing import Interpolator
from scan729 import scan729
    
cxn = labrad.connect()
dv = cxn.data_vault
dv.cd(['','Calibrations', 'Double Pass 729DP'])
dv.open(12)
data = dv.get().asarray
freq_interp =  data[:,0]
ampl_interp = data[:,1]
cxn.disconnect()
interp = Interpolator(freq_interp, ampl_interp)

freq_min = 160.0
freq_max = 250.0
freq_step = 1.0

freqs = numpy.arange(freq_min, freq_max + freq_step, freq_step)
freqs = numpy.clip(freqs, freq_min, freq_max)
ampls = interp.interpolated(freqs)
freqs = freqs.tolist()
ampls = ampls.tolist()

params = {
            'frequencies_729':freqs,
            'amplitudes_729': ampls,
            'doppler_cooling':10*10**-3,
            'heating_time':1.0e-3,
            'rabi_time':0.1e-3,#0.5*10**-3,
            'readout_time':5*10**-3,
            'repump_time':10*10**-3,
            'repump_854_ampl': -3.0,
            'repump_866_ampl': -11.0,
            'doppler_cooling_freq':103.0,
            'doppler_cooling_ampl':-11.0,
            'readout_freq':107.0,
            'readout_ampl':-11.0
        }
exprtParams = {
    'startNumber': 10,
    'iterations': 1
    }

analysis = {
    'threshold':30,
    }
exprt = scan729(params,exprtParams, analysis)
exprt.run()