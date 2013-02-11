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
    
    @staticmethod
    def sideband_addition(sideband_info, (wr1, wr2, wz, wmm)):
        sideband_name_map = {'radial 1': wr1, 
                             'radial 2': wr2,
                             'axial': wz,
                             'micromotion': wmm,
                             }
        d = dict(sideband_info)
        del d['min']
        del d['max']
        detuning = WithUnit(0,'MHz')
        for name, sideband in d.iteritems():
            detuning += int(round(sideband.value)) * sideband_name_map[name]
        return  detuning
    
    @staticmethod
    def saved_line_info_to_frequency_complete(line_info, line_selection, sideband_frequencies):
        line_selection = dict(line_selection[1])
        selected_line_name = line_selection.get('line')
        if selected_line_name is None: raise Exception ("could not find the selected line")
        freq = common_methods_729.saved_line_info_to_frequency(line_info, selected_line_name)
        for sideband in ['radial 1', 'radial 2', 'axial', 'micromotion']:
            freq += line_selection.get(sideband) * sideband_frequencies[sideband]
        return freq