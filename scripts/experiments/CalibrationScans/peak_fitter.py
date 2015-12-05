from scipy.optimize  import curve_fit
import numpy as np

class peak_fitter():
    
    def guess(self, f, p):
        '''
        just take the point at the peak value
        '''
        max_index = np.where(p == p.max())[0][0]
        fmax = f[max_index]
        if p.max() <= 0.2:
            raise Exception("Peak not found")
        else:
            # center, amplitude, width guesses
            return np.array([ fmax,  p.max(), 6e-3 ])
    def fit(self, f, p):
        model = lambda x, c0, a, w: a*np.exp(-(x - c0)**2/w**2)
        guess = self.guess(f, p)
        popt, copt = curve_fit(model, f, p, p0=guess)
        return popt[0] # just the fitted center value
