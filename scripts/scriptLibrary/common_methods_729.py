import numpy as np

class common_methods_729(object):
    
    @staticmethod
    def frequency_from_line_selection(frequency_selection, manual_frequency_729, line_selection, drift_tracker, lookup_needed = True):
        if not lookup_needed or frequency_selection == 'manual':
            return manual_frequency_729
        elif frequency_selection == 'auto':
            try:
                frequency = drift_tracker.get_current_line(line_selection)
                return frequency
            except Exception:
                raise Exception ("Unable to get {0} from drift tracker".format(line_selection))
        else:
            raise Exception ("Incorrect frequency selection")
    
    @staticmethod
    def add_sidebands(freq, sideband_selection, trap):
        sideband_frequencies = [trap.radial_frequency_1, trap.radial_frequency_2, trap.axial_frequency, trap.rf_drive_frequency]
        for order,sideband_frequency in zip(sideband_selection, sideband_frequencies):
            freq += order * sideband_frequency
        return freq
    
    @staticmethod
    def selected_sideband(sideband_selection):
        '''takes sideband selection like [0, 1, 0, 0] and returns the corresponding name of the sideband'''
        names = ['radial_frequency_1', 'radial_frequency_2', 'axial_frequency','rf_drive_frequency']
        selection_np = np.array(sideband_selection)
        if not np.count_nonzero(selection_np) == 1:
            raise Exception("Incorrect sideband selection")
        name = names[np.nonzero(selection_np)[0]]
        return name