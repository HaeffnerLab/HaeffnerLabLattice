class common_methods_729(object):
    
    @staticmethod
    def frequency_from_line_selection(frequency_selection, manual_frequency_729, line_selection, drift_tracker):
        if frequency_selection == 'manual':
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