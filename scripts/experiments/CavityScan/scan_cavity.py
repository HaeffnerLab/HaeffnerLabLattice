import labrad
from common.abstractdevices.script_scanner.scan_methods import experiment
from numpy import linspace
import time

class scan_cavity(experiment):
    
    name = 'Scan Cavity'
    required_parameters = [
                           ('CavityScans','average'),
                           ('CavityScans','cavity_name'),
                           ('CavityScans','cavity_scan'),
                           ('CavityScans','point_delay'),
                           ('CavityScans','moving_resolution'),
                           ]
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        cxnlab = labrad.connect('192.168.169.49')
        self.ld = cxnlab.laserdac
        self.pmt = cxn.normalpmtflow
        self.dv = cxn.data_vault
        self.average = int(self.parameters.CavityScans.average)
        self.cavity_name = self.parameters.CavityScans.cavity_name
        self.resolution = self.parameters.CavityScans.moving_resolution
        self.point_delay = self.parameters.CavityScans.point_delay['s']
        minim,maxim,steps = self.parameters.CavityScans.cavity_scan
        self.minim = minim = minim['mV']; self.maxim = maxim = maxim['mV']
        self.scan = linspace(minim, maxim, steps)
        self.init_voltage = self.ld.getvoltage(self.cavity_name)    
        self.navigate_data_vault()
        
    def navigate_data_vault(self):
        self.dv.cd(['','CavityScans'],True)
        self.dv.new('Cavity Scan {}'.format(self.cavity_name),[('Cavity Voltage', 'mV')], [('PMT Counts','Counts','Counts')] )
        self.dv.add_parameter('cavity channel', self.cavity_name)
        self.dv.add_parameter('plotLive',True)
    
    def run(self, cxn, context):
        steps = abs(self.init_voltage - self.minim) / float(self.resolution)
        #moving to beginning of scan
        self.current = self.init_voltage
        for voltage in linspace(self.init_voltage, self.minim, steps):
            self.ld.setvoltage(self.cavity_name,voltage)
            self.current = voltage
            time.sleep(self.point_delay)
            should_stop = self.pause_or_stop()
            if should_stop: return
        #performing scan
        for i,voltage in enumerate(self.scan):
            self.ld.setvoltage(self.cavity_name,voltage)
            self.current = voltage
            counts =  self.pmt.get_next_counts('ON',self.average,True)
            self.dv.add([voltage,counts])
            time.sleep(self.point_delay)
            should_stop = self.pause_or_stop()
            if should_stop: return
            self.update_progress(i)

    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.scan)
        self.sc.script_set_progress(self.ident,  progress)        
        
    def finalize(self, cxn, context):
        #back to inital voltage
        steps = abs(self.init_voltage - self.current) / float(self.resolution)
        for voltage in linspace(self.current, self.init_voltage, steps):
            self.ld.setvoltage(self.cavity_name,voltage)
            time.sleep(self.point_delay)  
            
if __name__ == '__main__':
    #normal way to launch
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = scan_cavity(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)