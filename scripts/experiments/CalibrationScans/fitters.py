from scipy.optimize import curve_fit
import numpy as np

class pi_time_fitter():

    def guess_tpi(self, t, exci):
        '''
        Start from the beginning of the flop.
        Use the starting guess as the first time
        the flop value goes down AND the flop has
        exceeded 0.9 excitation probability.
        '''

        last = 0
        for i, ex in enumerate(exci):
            if ex < last and last >= 0.9: return t[i-1]
            last = ex
        raise Exception('No valid pi time guess')

    def fit(self, t, exci):
        t0 = self.guess_tpi(t, exci)
        model = lambda x, tpi: np.sin(np.pi/2/tpi*np.array(x))**2
        t_pi, c = curve_fit(model, t, exci, p0 = t0)
        return t_pi[0]

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
