import numpy as np
import matplotlib
#matplotlib.use('Qt4Agg')
from matplotlib import pyplot

class correlator(object):
      
    @staticmethod
    def g2(intensity, resolution = 1, compute_range = None):
        '''
        computes g2 from the intensity array
        @var arr is the intensity array of intesnity per unit time
        @var time resolution of the intensity array
        '''
        intensity = np.array(intensity)
        N = intensity.size
        max_correlation_length = N / 3
        correlate_window = intensity[N/3 : 2*N/3 + 1] #middle third of the array
        g2 = []
        kk = []
        if compute_range == None:
            range_k = range(0, max_correlation_length)
        else:
            range_k = range(compute_range[0], compute_range[1])
        for k in range_k:
            #for each correlation length, offset the array and compute the product
            offset = intensity[N/3 + k: 2*N/3 + 1 + k]
            norm = max_correlation_length / float(np.sum(correlate_window) * np.sum(offset)) 
            prod = norm * np.dot(correlate_window, offset)
            g2.append(prod)
            kk.append(k)
        return np.array(kk), np.array(g2)    
                
if __name__ == '__main__':
    #g2 for a poisonnian process
    count_rate = 0.2
    samples = 2000.0
    photon_numbers = np.random.poisson(lam = count_rate, size = samples) #photon number is poisonian
    ks, result =  correlator.g2(photon_numbers, compute_range = None)
    pyplot.figure()
    pyplot.plot(ks, result)
    pyplot.show()