import numpy
from labrad import types as T
import time

'''Calibrates Double Passes'''

class double_pass_calibrator(object):
    def __init__(self, cxn, set_freq, set_ampl, get_reading, freq_info, ampl_info, name, average = 20):
        self.cxn = cxn
        self.set_freq = set_freq
        self.set_ampl = set_ampl
        self.get_reading = get_reading
        freq_min, freq_max, freq_steps = freq_info
        ampl_min, ampl_max, ampl_steps = ampl_info
        self.amplitudes = numpy.r_[ampl_min:ampl_max:complex(0,ampl_steps)]
        self.frequencies = numpy.r_[freq_min:freq_max:complex(0,freq_steps)]
        self.center_freq = (freq_min + freq_max) / 2.0
        self.ampl_max = ampl_max
        self.average = average
        self.name = name
        self.dv = cxn.data_vault
    
    def record(self):
        result = numpy.zeros(self.average)
        for j in range(len(result)):
            result[j] = self.get_reading()
        print result
        return numpy.average(result)
    
    def ampl_scan(self, freq):
        '''performs the amplitude scan at a given frequency'''
        self.set_freq(T.Value(freq, 'MHz'))
        time.sleep(2.0)
        readout = numpy.zeros_like(self.amplitudes)
        for i,ampl in enumerate(self.amplitudes):
            print 'ampl {}'.format(ampl)
            self.set_ampl(T.Value(ampl,'dBm'))
            reading = self.record()
            readout[i] = reading
        return readout
        
    def freq_scan(self, ampl):
        '''performs the frequency scan at a given amplitude'''
        self.set_ampl(T.Value(ampl,'dBm'))
        time.sleep(2.0)
        readout = numpy.zeros_like(self.frequencies)
        for i,freq in enumerate(self.frequencies):
            print 'freq {}'.format(freq)
            self.set_freq(T.Value(freq, 'MHz'))
            reading = self.record()
            readout[i] = reading
        return readout
    
    def do_calibration_decoupled(self, set_point_ratio = 1.0):
        '''performs the calibration by assuming that the calibration of the light intensity vs AO power is frequency independent
        This allows to do two separate scans: intensity vs frequency and intensity vs amplitude and then combine the results'''
        dv = self.dv
        #do the scans first
        ampl_scan = self.ampl_scan(self.center_freq)
        freq_scan = self.freq_scan(self.ampl_max)
        #save the scans
        dv.cd(['','Calibrations','Double Pass {}'.format(self.name)],True)
        dv.new('{0} double pass power scan at freq {1}'.format(self.name, self.center_freq ),[('power','dBM')],[('power','power','W')])
        data = numpy.vstack((self.amplitudes, ampl_scan)).transpose()
        dv.add_parameter('plotLive', True)
        dv.add(data)
        dv.new('{0} double frequency scan at ampl {1}'.format(self.name, self.ampl_max ),[('freq','MHz')],[('power','power','W')])
        data = numpy.vstack((self.frequencies, freq_scan)).transpose()
        dv.add_parameter('plotLive', True)
        dv.add(data)  
        #find setpoint
        min_count = freq_scan.min()
        set_point = min_count * set_point_ratio
        #normalize amplutde scan
        ampl_scan_norm = ampl_scan / ampl_scan.max() 
        #do the calibration by finding, for every frequency, the power needed to bring the level to the setpoint
        calibration = []
        for index, freq in enumerate(self.frequencies):
            if freq_scan[index] == 0: raise Exception ("recorded 0 intensity at {} MHz".format(freq))
            relativeLevelNeeded = set_point / freq_scan[index]
            closestPower = self.amplitudes[(numpy.abs(ampl_scan_norm - relativeLevelNeeded)).argmin()]
            calibration.append([freq, closestPower])
        print calibration
        dv.cd(['','Calibrations','Double Pass {}'.format(self.name)],True)
        dv.new('{0} calibration decoupled'.format(self.name),[('freq','MHz')],[('power','power','dBm')])
        dv.add_parameter('plotLive', True)
        dv.add(calibration)

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    freq_info = (90.0, 130.0, 100) #min, max, steps, freqs in MHz
    ampl_info = (-15.0, -11.0, 100) #mapl in dBm
    average = 50
    name = '110DP'
    pm = cxn.power_meter_server
    pm.select_device(0)
    pm.auto_range()
    get_reading = pm.measure
    dds = cxn.pulser
    dds.select_dds_channel(name)
    set_ampl = dds.amplitude
    set_freq = dds.frequency
    calib = double_pass_calibrator(cxn, set_freq, set_ampl, get_reading, freq_info, ampl_info, name, average)
    calib.do_calibration_decoupled()
    print 'DONE'