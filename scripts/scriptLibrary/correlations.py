import numpy
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

class correlator(object):
    
    @staticmethod
    def g2_differences(arr):
        '''
        computes differences between pairs of elements
         
        '''
        differences = []
        
        for i in range(len(arr)):
            for j in range(len(arr)):
                if not i == j:
                    differences.append(arr[i] - arr[j])
        return numpy.array(differences)             

if __name__ == '__main__':
    #g2 for a poisonnian process
    count_rate = 5.0
    samples = 2000.0
    photon_numbers = numpy.random.poisson(lam = count_rate, size = samples) #photon number is poisonian
    timetags = []
    for i,num in enumerate(photon_numbers):
        if num > 0:
            timetags.extend(num * [i])
    diffs = correlator.element_differences(timetags)
    pyplot.hist(diffs, 500)
    pyplot.show()
    #g2 for a poisonnian process with 
    