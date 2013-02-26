import labrad
from numpy import linspace
from common.abstractdevices.script_scanner.scan_methods import experiment
from fft_peak_area import fft_peak_area

class fft_hv_scan(experiment):
    
    name = 'FFT Scan High Volt'
    required_parameters = [
                           ('FFT','scan_hv_vs_fft')
                           ]
    required_parameters.extend(fft_peak_area.required_parameters)
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.script = self.make_experiment(fft_peak_area)
        self.script.initialize(cxn, context, ident)
        minim,maxim,steps = self.parameters.FFT.scan_hv_vs_fft
        minim = minim['V']; maxim = maxim['V']
        self.scan = linspace(minim, maxim, steps)
        self.dv = cxn.data_vault
        self.hv = cxn.highvolta
        self.init_voltage  = self.hv.getvoltage()
        self.navigate_data_vault(self.dv)
        
    def navigate_data_vault(self, dv):
        dv.cd(['','QuickMeasurements','FFT'],True)
        name = dv.new('FFT',[('Voltage', 'V')], [('FFTPeak','Arb','Arb')] )
        dv.add_parameter('plotLive',True)

    def run(self, cxn, context):
        for i,voltage in enumerate(self.scan):
            self.hv.setvoltage(voltage)
            self.set_script_progress_limits(i)
            area = self.script.run(cxn, context)
            self.dv.add(voltage, area)
            self.update_progress(i)
            if self.script.should_stop: return
    
    def set_script_progress_limits(self, i):
        self.script.set_progress_limits(100.0 * i / len(self.scan), 100.0 * (i + 1) / len(self.scan))
    
    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.scan)
        self.sc.script_set_progress(self.ident,  progress)
        
    def finalize(self, cxn, context):
        self.hv.setvoltage(self.init_voltage)
        self.script.finalize(cxn, context)

if __name__ == '__main__':
    #normal way to launch
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = fft_hv_scan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)