from fft_spectrum import fft_spectrum, labrad

class fft_peak_area(fft_spectrum):
    
    name = 'FFT Peak Area'
    required_parameters = [
                           ('TrapFrequencies','rf_drive_frequency'),
                           ('FFT','average'),
                           ('FFT','frequency_offset'),
                           ('FFT','frequency_span'),
                           ('FFT','record_time'),
                           ('FFT','peak_width_pts')
                           ]

    def run(self, cxn, context):
        pts_around = int(self.parameters.FFT.peak_width_pts)
        try:
            peak_area = self.getPeakArea(pts_around)
        except Exception:
            print 'peak not found'
            peak_area = -1.0
        print 'peak area', peak_area
        return peak_area

if __name__ == '__main__':
    #normal way to launch
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = fft_peak_area(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)