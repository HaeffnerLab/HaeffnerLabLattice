from LatentHeatGlobal import LatentHeat
for delay in [7500e-3, 10000e-3, 15000e-3, 20000e-3, 30000e-3]:
    params = {
        'initial_cooling': 25e-3,###DO NOT CHANGE
        'heat_delay':10e-3,###DO NOT CHANGE
        'axial_heat':100*10**-9,
        'readout_delay':delay,
        'readout_time':10.0*10**-3,###DO NOT CHANGE
        'xtal_record':100e-3,
        'cooling_ampl_866':-3.0,
        'heating_ampl_866':-3.0,
        'readout_ampl_866':-3.0,
        'xtal_ampl_866':-3.0,
        'cooling_freq_397':103.0,
        'cooling_ampl_397':-13.5,
        'readout_freq_397':115.0,
        'readout_ampl_397':-13.5,
        'xtal_freq_397':103.0,
        'xtal_ampl_397':-11.0,
        'heating_freq_397':130.0,
        'heating_ampl_397':-63.0,
    }
    exprtParams = {
       'iterations':200,
       'rf_power':-3.5, #### make optional
       'rf_settling_time':0.3,
       'auto_crystal':True,
       'pmtresolution':0.075,
       'detect_time':0.225,
       'binTime':250.0*10**-6,
       'threshold':40000
    }
    exprt = LatentHeat(params,exprtParams)
    exprt.run()