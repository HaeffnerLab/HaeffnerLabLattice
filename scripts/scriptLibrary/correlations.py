import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

class correlator(object):
    
    @staticmethod
    def element_differences(arr, bins):
        '''
        computes differences between all pairs of elements from an array of timetags
        
        maximum correlation is one third of the timetag duration. 
        this way, time differences are computed from the the middle third of timetags never lie outside the given range. 
        '''
        arr = np.array(arr)
        arr_length = arr.max() - arr.min()
        arr_center = arr.min() + arr_length / 2.0
        max_correlation_length = arr_length / 3.0
        #correlate_window are timetags with which all differences are computed. 
        #correlate_window is max_correlation_length-wide. centered in the middle of timetags
        start_correlate_window = (arr_center - max_correlation_length/2.0)
        stop_correlate_window = (arr_center + max_correlation_length/2.0)
        correlate_where = (arr >= start_correlate_window) * (arr <= stop_correlate_window)
        correlate_window = arr[correlate_where]
        #rearangeing all timetags so that they start with timteags from correlate_window. this helps with indexing.
        all_timetags = list(correlate_window)
        all_timetags.extend(arr[np.logical_not(correlate_where)])
        differences = []
        for i in range(len(correlate_window)):
            for j in range(len(all_timetags)):
                diff = correlate_window[i] - all_timetags[j]
                if 0 <= diff < max_correlation_length:
                    differences.append(diff)
        return differences

if __name__ == '__main__':
    #g2 for a poisonnian process
    count_rate = 0.01
    samples = 30000.0
    photon_numbers = np.random.poisson(lam = count_rate, size = samples) #photon number is poisonian
    
    timetags = []
    for i,num in enumerate(photon_numbers):
        if num > 0:
            timetags.extend(num * [i])
    differences = correlator.element_differences(timetags, 500)
    
#    average =  np.mean(photon_numbers)
#    print np.bincount(photon_numbers)
#    print 'average', average
#    
#    print np.mean(photon_numbers**2) / float(np.mean(photon_numbers)**2)
    
    from correlations_2 import correlator as corr2
    
    ks, result =  corr2.g2(photon_numbers, compute_range = None)
    

    pyplot.figure()
    pyplot.plot(ks, result)
    ct = np.bincount(differences)
    pyplot.plot(ct / np.mean(ct))
    pyplot.show()
    hist,bins = correlator.element_differences(timetags, 500)
    pyplot.bar(bins[:-1], hist, width = bins[1]-bins[0])
    pyplot.show()
#    g2 for a poisonnian process with 