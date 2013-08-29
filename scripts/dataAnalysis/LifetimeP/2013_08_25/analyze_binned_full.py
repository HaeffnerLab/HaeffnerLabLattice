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
background_domain = (0.0, 3.0)
background_where = np.where((background_domain[0] <= bins) * (bins <= background_domain[1]))
background_bins,background_counts = bins[background_where], hist[background_where]
background_total = background_counts.sum()
#print background_total
background_level = background_total / float(background_bins.size)
background_level_sigma = np.sqrt(np.sum(background_total)) /  float(background_bins.size)
print 'Calculated background level to be {0:.2f} with sigma of {1:.2f}, relative uncertainty {2:.2e}'.format(background_level, background_level_sigma, background_level_sigma / background_level)

#calculate the area of 866 peak
peak_866 = (17, 46)
peak_866_where = np.where((peak_866[0] <= bins) * (bins <= peak_866[1]))
peak_866_bins,peak_866_counts = bins[peak_866_where], hist[peak_866_where]
area_866_sigma = np.sqrt(np.sum(peak_866_counts))
print 'With background, 866 peak is {0:.3e} with sigma {1:.2e}, relative uncertainty {2:.2e}'.format(peak_866_counts.sum(), area_866_sigma, area_866_sigma / peak_866_counts.sum())

#subtracking background per bin
#print peak_866_counts
background_subtrated_866_area = np.sum(peak_866_counts - background_level)
total_uncertainty_of_background = background_level_sigma * peak_866_counts.size

background_subtrated_866_sigma = np.sqrt( area_866_sigma**2 +  (total_uncertainty_of_background)**2 )
toprint =  'Background-subtracted area of 866 is {0:.4e}, with uncertainty {1:.2e} with contribution from area {2:.2e} and background estimation {3:.2e}. Relative uncertainty is {4:.2e}'
summary_866 = 'Area 866:  {0:.1e}, relative uncertainty {4:.1e}'
print toprint.format(background_subtrated_866_area, background_subtrated_866_sigma, area_866_sigma, total_uncertainty_of_background, background_subtrated_866_sigma / background_subtrated_866_area)
summary_866 = summary_866.format(background_subtrated_866_area, background_subtrated_866_sigma, area_866_sigma, total_uncertainty_of_background, background_subtrated_866_sigma / background_subtrated_866_area)


##finds collection efficiency, here needs access to completed sequences, ion number
#completed_sequences = 527 *  1000 * 84
#collection_efficiency = background_subtrated_866_area / (c.ion_number * completed_sequences)

#pyplot.plot(bins, hist, '.k', markersize=0.7)
#pyplot.annotate(collection_str, xy=(0.55, 0.85), xycoords='axes fraction')
#pyplot.annotate(summary_866, xy=(0.55, 0.95), xycoords='axes fraction')

#pyplot.ylim(ymin = 0)
#pyplot.xlabel(u'Time \265s')
#pyplot.ylabel('Photons per bin of 10 ns')
#pyplot.show()