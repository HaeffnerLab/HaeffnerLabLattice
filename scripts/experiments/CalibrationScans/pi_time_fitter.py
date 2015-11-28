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

        

