class Test():
        scannable_params = {
        #'Spectrum.carrier_detuning':  [(-50, 50, 100, 'kHz'), 'window']
        'Spectrum.carrier_detuning' : [(-150, 150, 10, 'kHz'),'spectrum'],
        'Spectrum.sideband_detuning' :[(-50, 50, 100, 'kHz'),'spectrum']
              }
        
        @classmethod
        def get_scannable_params(cls):
            return cls.scannable_params
        
print Test.get_scannable_params()