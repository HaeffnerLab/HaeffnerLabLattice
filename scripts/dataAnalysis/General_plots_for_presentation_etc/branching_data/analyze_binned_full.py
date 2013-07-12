from __future__ import division
import numpy as np
import matplotlib
#from constants import constants as c

from matplotlib import pyplot
from scipy.optimize import curve_fit
#load binned information from the file
#data in the form of [filename , total transfers , sequences per transfer, cycles per sequence]
data = [
        ['1329_33.npy', 1001, 1500, 50],
        ['2018_08_first.npy', 370, 1500, 50],
        ['2018_08_second.npy', 380, 1500, 50],         
         ]
pmt_deadtime = 16.5*10**-9 * 1
binned_resolution = 10**-8 #10ns
data_arrays = []
for datafile, transfers, seq_per_transfer, cycles_per_seq in data:
    #load
    arr = np.load(datafile)
    #deadtime correction
    recordtime_per_bin = binned_resolution * cycles_per_seq * seq_per_transfer * transfers
    arr[:,1] = arr[:,1] / (1- pmt_deadtime *arr[:,1]/recordtime_per_bin)
    data_arrays.append(arr)


bins = data_arrays[0][:,0]*1e6 #time now in mus
hist_arrays = tuple([arr[:,1] for arr in data_arrays])
hist = np.sum(np.vstack(hist_arrays), axis = 0)


#find the background level
background_domain = (81.0, 86.0)
background_where = np.where((background_domain[0] <= bins) * (bins <= background_domain[1]))
background_bins,background_counts = bins[background_where], hist[background_where]
background_total = background_counts.sum()
background_level = background_total / background_bins.size
background_level_sigma = np.sqrt(background_level / background_bins.size)
print 'background level: {0:.2f}, sigma {1:.2f}, relative sigma {2:.2e}'.format(background_level, background_level_sigma, background_level_sigma / background_level)

#calculate the area of 866 peak
peak_866 = (86.0, 100)
peak_866_where = np.where((peak_866[0] <= bins) * (bins <= peak_866[1]))
peak_866_bins,peak_866_counts = bins[peak_866_where], hist[peak_866_where]
peak_866_with_background = np.sum(peak_866_counts)
area_866_sigma = np.sqrt(peak_866_with_background)
#subtracking background per bin
background_subtrated_866_area = peak_866_with_background - peak_866_counts.size * background_level
background_subtrated_866_sigma = np.sqrt( area_866_sigma**2 +  (peak_866_counts.size * background_level_sigma)**2 )
toprint =  'N_r {0:.6e}, total sigma {1:.2e} sigma from area {2:.2e} and sigma background {3:.2e}. Relative sigma {4:.2e}'
summary_866 = 'Area 866:  {0:.4e}, relative uncertainty {4:.4e}'
print toprint.format(background_subtrated_866_area, background_subtrated_866_sigma, area_866_sigma, peak_866_counts.size * background_level_sigma, background_subtrated_866_sigma / background_subtrated_866_area)
summary_866 = summary_866.format(background_subtrated_866_area, background_subtrated_866_sigma, area_866_sigma, peak_866_counts.size * background_level_sigma, background_subtrated_866_sigma / background_subtrated_866_area)
##finds collection efficiency, here needs access to completed sequences, ion number
#completed_sequences = 527 *  1000 * 84
#collection_efficiency = background_subtrated_866_area / (c.ion_number * completed_sequences)
#collection_str = 'Collection efficiency {:.1e} per ion'.format(collection_efficiency)
#computing the area of the 397 peak
peak_397_domain = (5.0, 45.0)
peak_397_where = np.where((peak_397_domain[0] <= bins) * (bins <= peak_397_domain[1]))
peak_397_bins,peak_397_counts = bins[peak_397_where], hist[peak_397_where]
peak_397_area = np.sum(peak_397_counts)
peak_397_area_sigma = np.sqrt(peak_397_area)
#corresponding background of area of the 397 peak
background_397_domain = (45.0, 85.0)
background_397_domain_where = np.where((background_397_domain[0] <= bins) * (bins <= background_397_domain[1]))
background_397_bins, background_397_counts = bins[background_397_domain_where], hist[background_397_domain_where]
background_397_area = np.sum(background_397_counts)
background_397_sigma = np.sqrt(background_397_area)
background_subtracted_397_area = peak_397_area - background_397_area
background_subtracted_397_area_sigma = np.sqrt(peak_397_area_sigma**2 + background_397_sigma**2)
print 'N_b {0:.2e} with sigma {1:.2e} relative sigma of {2:.2e}'.format(background_subtracted_397_area , background_subtracted_397_area_sigma, background_subtracted_397_area_sigma / background_subtracted_397_area)
summary_397 = 'Area 397:  {0:.1e}, relative uncertainty {2:.1e}'.format(background_subtracted_397_area , background_subtracted_397_area_sigma, background_subtracted_397_area_sigma / background_subtracted_397_area)

#find the branching fraction
branching_fraction = background_subtracted_397_area / (background_subtracted_397_area + background_subtrated_866_area)
z = background_subtrated_866_area / background_subtracted_397_area
branching_fraction_error = branching_fraction**2 * z * np.sqrt((background_subtracted_397_area_sigma/background_subtracted_397_area)**2 + (background_subtrated_866_sigma/background_subtrated_866_area)**2)
branching_str = u'Branching: {0:.5f} \261 {1:.5f}'.format(  branching_fraction, branching_fraction_error)
print 'Uncorrected fraction', branching_str
#pyplot.plot(bins, hist, '.k', markersize=0.7)
pyplot.plot(bins, hist, markersize=0.7)
pyplot.annotate(branching_str, xy=(0.55, 0.80), xycoords='axes fraction')
#pyplot.annotate(collection_str, xy=(0.55, 0.85), xycoords='axes fraction')
pyplot.annotate(summary_866, xy=(0.55, 0.95), xycoords='axes fraction')
pyplot.annotate(summary_397, xy=(0.55, 0.90), xycoords='axes fraction')

pyplot.ylim(ymin = 0)
pyplot.title('Branching Ratio 13 ions')
pyplot.xlabel(u'Time \265s')
pyplot.ylabel('Photons per bin of 10 ns')

systematic_limit_397 = 1.36356467395e-06
systematic_limit_866 = -1.59713328508e-05
print 'limit correction', systematic_limit_397 + systematic_limit_866
corrected_branching = branching_fraction + systematic_limit_397 + systematic_limit_866


print corrected_branching, 1 - corrected_branching


biref_error = branching_fraction_error
pmt_error = 3e-6
lifetime_error = 2e-6
extinction_error = 5e-6
duration_error = 6e-6
combined_error = np.sqrt(branching_fraction_error**2 +  biref_error**2 + pmt_error**2 + lifetime_error**2 + extinction_error**2 + duration_error**2)
branching_str_corrected = u'Branching With Sys: {0:.5f} \261 {1:.5f}'.format(  corrected_branching, combined_error)
print 'Uncorrected fraction', branching_str_corrected
pyplot.annotate(branching_str_corrected, xy=(0.55, 0.70), xycoords='axes fraction')

pyplot.show()