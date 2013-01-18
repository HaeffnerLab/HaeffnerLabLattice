import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

class correlator(object):
      
    @staticmethod
    def g2(intensity, compute_range = None):
        '''
        computes g2 from the intensity array
        @var arr is the intensity array of photon counts per unit time, such as [1, 0, 3, 4 ,...]
        '''
        intensity = np.array(intensity)
        N = intensity.size
        max_correlation_length = np.floor_divide(N , 2)
        correlate_window = intensity[ : max_correlation_length]
        g2 = []
        kk = []
        if compute_range == None:
            range_k = range(0, max_correlation_length + 1)
        else:
            range_k = range(0, compute_range)
        for k in range_k:
            print k
            #for each correlation length, offset the array and compute the product
            moving_window = intensity[k : max_correlation_length + k]
            product = np.mean(moving_window * correlate_window)
            normalized = product / (np.mean(correlate_window) * np.mean(moving_window))
            g2.append(normalized)
            kk.append(k)
        #special case for k = 0:
        g2[0] = np.mean(correlate_window * (correlate_window - 1)) / (np.mean(correlate_window)**2)
        return np.array(kk), np.array(g2)
                
if __name__ == '__main__':
    #g2 for a poisonnian process
    count_rate = 1 / 500.0
    samples = 1.0 / count_rate * 30000
    average = 100
    max_k = 10
    result = np.zeros(max_k)
    for i in range(average):
        print 'average', i
        photon_numbers = np.random.poisson(lam = count_rate, size = samples) #photon number is poisonian
        ks, res =  correlator.g2(photon_numbers, max_k)
        result += res
    result = result / average
    pyplot.plot(ks, result)
    pyplot.show()