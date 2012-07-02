from LatentHeat import LatentHeat
for delay in [100e-3,500e-3]:#, 1000e-3,2000e-3, 3000e-3, 4000e-3, 5000e-3, 7500e-3, 10000e-3]:
    params = {
        'initial_cooling': 25e-3,
        'heat_delay':10e-3,###DO NOT CHANGE
        'axial_heat':100e-9,
        'readout_delay':delay,
        'readout_time':10.0*10**-3,
        'xtal_record':100e-3,
        'cooling_ampl_866':-11.0,
        'heating_ampl_866':-11.0,
        'readout_ampl_866':-11.0,
        'xtal_ampl_866':-11.0,
        'cooling_freq_397':103.0,
        'cooling_ampl_397':-13.5,
        'readout_freq_397':115.0,
        'readout_ampl_397':-13.5,
        'xtal_freq_397':103.0,
        'xtal_ampl_397':-11.0,
    }
    exprtParams = {
       'iterations':25,
       'rf_power':-3.5, #### make optional
       'rf_settling_time':0.3,
       'auto_crystal':True,
       'pmtresolution':0.075,
       'detect_time':0.225,
       'binTime':250.0*10**-6,
       'threshold':35000
    }
    exprt = LatentHeat(params,exprtParams)
    exprt.run()