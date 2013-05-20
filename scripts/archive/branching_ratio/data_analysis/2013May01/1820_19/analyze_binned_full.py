import numpy as np
import matplotlib
from constants import constants as c

from matplotlib import pyplot

#load binned information from the file
f = np.load(c.bin_filename)
bins = f[:,0]
hist = f[:,1]
bins = bins*1e6 #time now in mus

#hist = hist/(1-1.65*hist/(1001*1500*50))

#find the background level
background_domain = (0.0, 6.0)
background_where = np.where((background_domain[0] <= bins) * (bins <= background_domain[1]))
background_bins,background_counts = bins[background_where], hist[background_where]
background_total = background_counts.sum()
background_level = background_total / float(background_bins.size)
background_level_sigma = np.sqrt(np.sum(background_total)) /  float(background_bins.size)
print 'Calculated background level to be {0:.2f} with sigma of {1:.2f}, relative uncertainty {2:.2e}'.format(background_level, background_level_sigma, background_level_sigma / background_level)

#calculate the area of 866 peak
peak_866 = (105.0, 165.0)
peak_866_where = np.where((peak_866[0] <= bins) * (bins <= peak_866[1]))
peak_866_bins,peak_866_counts = bins[peak_866_where], hist[peak_866_where]
area_866_sigma = np.sqrt(np.sum(peak_866_counts))
print 'With background, 866 peak is {0:.2e} with sigma {1:.2e}, relative uncertainty {2:.2e}'.format(peak_866_counts.sum(), area_866_sigma, area_866_sigma / peak_866_counts.sum())

#subtracking background per bin
background_subtrated_866_area = np.sum(peak_866_counts - background_level)
total_uncertainty_of_background = background_level_sigma * peak_866_counts.size

background_subtrated_866_sigma = np.sqrt( area_866_sigma**2 +  (total_uncertainty_of_background)**2 )
toprint =  'Background-subtracted area of 866 is {0:.2e}, with uncertainty {1:.2e} wiht contribuation from area {2:.2e} and background estimation {3:.2e}. Relative uncertainy is {4:.2e}'
summary_866 = 'Area 866:  {0:.1e}, relative uncertainty {4:.1e}'
print toprint.format(background_subtrated_866_area, background_subtrated_866_sigma, area_866_sigma, total_uncertainty_of_background, background_subtrated_866_sigma / background_subtrated_866_area)
summary_866 = summary_866.format(background_subtrated_866_area, background_subtrated_866_sigma, area_866_sigma, total_uncertainty_of_background, background_subtrated_866_sigma / background_subtrated_866_area)


##finds collection efficiency, here needs access to completed sequences, ion number
#completed_sequences = 527 *  1000 * 84
#collection_efficiency = background_subtrated_866_area / (c.ion_number * completed_sequences)
#collection_str = 'Collection efficiency {:.1e} per ion'.format(collection_efficiency)

#computing the area of the 397 peak
peak_397_domain = (5.0, 55.0)
peak_397_where = np.where((peak_397_domain[0] <= bins) * (bins <= peak_397_domain[1]))
peak_397_bins,peak_397_counts = bins[peak_397_where], hist[peak_397_where]
peak_397_area = np.sum(peak_397_counts)
peak_397_area_sigma = np.sqrt(peak_397_area)

#corresponding background of area of the 397 peak
background_397_domain = (55.0, 105.0)
background_397_domain_where = np.where((background_397_domain[0] <= bins) * (bins <= background_397_domain[1]))
background_397_bins, background_397_counts = bins[background_397_domain_where], hist[background_397_domain_where]
background_397_area = np.sum(background_397_counts)
background_397_sigma = np.sqrt(background_397_area)

background_subtracted_397_area = peak_397_area - background_397_area
background_subtracted_397_area_sigma = np.sqrt(peak_397_area_sigma**2 + background_397_sigma**2)
print '397 background subtracted area is {0:.2e} with unceratiny of {1:.2e} or relative uncertainty of {2:.2e}'.format(background_subtracted_397_area , background_subtracted_397_area_sigma, background_subtracted_397_area_sigma / background_subtracted_397_area)
summary_397 = 'Area 397:  {0:.1e}, relative uncertainty {2:.1e}'.format(background_subtracted_397_area , background_subtracted_397_area_sigma, background_subtracted_397_area_sigma / background_subtracted_397_area)
z = (background_subtracted_397_area / background_subtrated_866_area)
branching = z / (z + 1)
branching_error = branching * np.sqrt( (background_subtracted_397_area_sigma / background_subtracted_397_area)**2  + (background_subtrated_866_sigma / background_subtrated_866_area)**2  )/z
branching_str = u'Branching: {0:.5f} \261 {1:.5f}'.format(  branching, branching_error) 


pyplot.plot(bins, hist, '.k', markersize=0.7)
pyplot.annotate(branching_str, xy=(0.55, 0.80), xycoords='axes fraction')
#pyplot.annotate(collection_str, xy=(0.55, 0.85), xycoords='axes fraction')
pyplot.annotate(summary_866, xy=(0.55, 0.95), xycoords='axes fraction')
pyplot.annotate(summary_397, xy=(0.55, 0.90), xycoords='axes fraction')

pyplot.ylim(ymin = 0)
pyplot.title('Branching Ratio {0}, {1:.0f} ions'.format(c.bin_filename,c.ion_number))
pyplot.xlabel(u'Time \265s')
pyplot.ylabel('Photons per bin of 10 ns')
pyplot.show()