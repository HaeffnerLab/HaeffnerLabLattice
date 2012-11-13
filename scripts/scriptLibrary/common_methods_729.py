import numpy as np
from labrad.units import WithUnit

class common_methods_729(object):
    
    @staticmethod
    def saved_line_info_to_scan(info, line_name):
        '''
        takes the saved line information and convets it to a a list of frequencies
        return the list of frequencies, amplitude, and excitation_duration
        '''
        try:
            min_freq = info[0][1]['MHz']
            max_freq = info[1][1]['MHz']
            line_info = [line_info for line_info in info if line_info[0] == line_name ][0]
        except KeyError:
            raise Exception ("{0} line not found in the provides information".format(line_name))
        else:
            center = line_info[1]['MHz']
            span = line_info[2]['MHz']
            resolution = line_info[3]['MHz']
            points = max(1, span / resolution)
            start = center - span/2.0
            stop = center + span/2.0
            print span, resolution
            scan_unitless = np.linspace(start, stop, points)
            if not ((min_freq <= scan_unitless)*(scan_unitless <= max_freq)).all():
                raise Exception ("Some frequency points are beyond allowed range")
            scan = [WithUnit(s, 'MHz') for s in scan_unitless] #assign units back to the scan
            amplitude = line_info[4]
            excitation_duration = line_info[5]
        return scan, amplitude, excitation_duration
    
    @staticmethod
    def saved_line_info_to_frequency(info, line_name):
        try:
            min_freq = info[0][1]
            max_freq = info[1][1]
            line_info = [line_info for line_info in info if line_info[0] == line_name ][0]
        except KeyError:
            raise Exception ("{0} line not found in the provides information".format(line_name))
        else:
            center = line_info[1]
            assert min_freq<=center<=max_freq, "Some frequency points are beyond allowed range"
        return center