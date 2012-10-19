#load the file
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
binned_file = '00001 - Timetags 2012Oct16_2036_59_binned.npy'
f = np.load(binned_file)
bins = f[:,0]
hist = f[:,1]

#find the background level
background_domain = (0, 20e-6)
background_where = np.where((background_domain[0] <= bins) * (bins <= background_domain[1]))
background_bins,background_counts = bins[background_where], hist[background_where]
background_total = background_counts.sum()
background_level = background_total / float(background_bins.size)
background_level_sigma = np.sqrt(np.sum(background_total)) /  float(background_bins.size)
print 'Calculated background level to be {0:.2f} with sigma of {1:.2f}, relative uncertainty {2:.2e}'.format(background_level, background_level_sigma, background_level_sigma / background_level)

#calculate the area of 866 peak
peak_866 = (61.0e-6, 65.0e-6)
peak_866_where = np.where((peak_866[0] <= bins) * (bins <= peak_866[1]))
peak_866_bins,peak_866_counts = bins[peak_866_where], hist[peak_866_where]
area_866_sigma = np.sqrt(np.sum(peak_866_counts))
print 'Total Area Under 866 peak is {0:.2e} with sigma {1:.2e}, relative uncertainty {2:.2e}'.format(peak_866_counts.sum(), area_866_sigma, area_866_sigma / peak_866_counts.sum())

##subtracking background per bin
background_subtrated_866_area = np.sum(peak_866_counts - background_level)
total_uncertainty_of_background = background_level_sigma * peak_866_counts.size

background_subtrated_866_sigma = np.sqrt( area_866_sigma**2 +  (total_uncertainty_of_background)**2 )
toprint =  'Background subtracted area is {0:.2e}, with uncertainty {1:.2e} wiht contribuation from area {2:.2e} and background estimation {3:.2e}. Relative uncertainy is {4:.2e}'
print toprint.format(background_subtrated_866_area, background_subtrated_866_sigma, area_866_sigma, total_uncertainty_of_background, background_subtrated_866_sigma / background_subtrated_866_area)

completed_sequences = 360e6 * 0.93 
collection_efficiency = background_subtrated_866_area / completed_sequences
print 'Estimated collection efficiency is {:.1e}'.format(collection_efficiency)

pyplot.plot(bins, hist)
pyplot.title('Branching Ratio ' + binned_file)
pyplot.xlabel(u'Time \265s')
pyplot.ylabel('Photons per bin of {}s'.format(bins.size))
pyplot.show()