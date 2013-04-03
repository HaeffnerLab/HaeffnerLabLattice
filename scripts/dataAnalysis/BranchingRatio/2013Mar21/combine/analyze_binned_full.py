import numpy as np
import matplotlib
#from constants import constants as c
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

#load binned information from the file
f1 = np.load('1329_33.npy')
f2 = np.load('1759_37.npy')
f3 = np.load('1826_35.npy')
f4 = np.load('1857_30.npy')
f5 = np.load('2018_08_first.npy')
f6 = np.load('2018_08_second.npy')

bins = f1[:,0]

f1[:,1] = f1[:,1]/(1-1.65*f1[:,1]/(1001*1500*50))
f2[:,1] = f2[:,1]/(1-1.65*f2[:,1]/(100*1500*50))
f3[:,1] = f3[:,1]/(1-1.65*f3[:,1]/(100*1500*50))
f4[:,1] = f4[:,1]/(1-1.65*f4[:,1]/(300*1500*50))
f5[:,1] = f5[:,1]/(1-1.65*f5[:,1]/(370*1500*50))
f6[:,1] = f6[:,1]/(1-1.65*f6[:,1]/(380*1500*50))


#hist = f1[:,1]+f2[:,1]+f3[:,1]+f4[:,1]+f5[:,1]+f6[:,1]

hist = f1[:,1]+f5[:,1]+f6[:,1]

bins = bins*1e6 #time now in mus

#hist = hist/(1-1.65*hist/(1001*1500*50))

#find the background level
background_domain = (81.0, 86.0)
background_where = np.where((background_domain[0] <= bins) * (bins <= background_domain[1]))
background_bins,background_counts = bins[background_where], hist[background_where]
background_total = background_counts.sum()
background_level = background_total / float(background_bins.size)
background_level_sigma = np.sqrt(np.sum(background_total)) /  float(background_bins.size)
print 'Calculated background level to be {0:.2f} with sigma of {1:.2f}, relative uncertainty {2:.2e}'.format(background_level, background_level_sigma, background_level_sigma / background_level)

#calculate the area of 866 peak
peak_866 = (86.0, 100.0)
peak_866_where = np.where((peak_866[0] <= bins) * (bins <= peak_866[1]))
peak_866_bins,peak_866_counts = bins[peak_866_where], hist[peak_866_where]
area_866_sigma = np.sqrt(np.sum(peak_866_counts))
print 'With background, 866 peak is {0:.2e} with sigma {1:.2e}, relative uncertainty {2:.2e}'.format(peak_866_counts.sum(), area_866_sigma, area_866_sigma / peak_866_counts.sum())

#subtracking background per bin
background_subtrated_866_area = np.sum(peak_866_counts - background_level)
total_uncertainty_of_background = background_level_sigma * peak_866_counts.size

background_subtrated_866_sigma = np.sqrt( area_866_sigma**2 +  (total_uncertainty_of_background)**2 )
toprint =  'Background-subtracted area of 866 is {0:.2e}, with uncertainty {1:.2e} wiht contribuation from area {2:.2e} and background estimation {3:.2e}. Relative uncertainy is {4:.2e}'
summary_866 = 'Area 866:  {0:.4e}, relative uncertainty {4:.4e}'
print toprint.format(background_subtrated_866_area, background_subtrated_866_sigma, area_866_sigma, total_uncertainty_of_background, background_subtrated_866_sigma / background_subtrated_866_area)
summary_866 = summary_866.format(background_subtrated_866_area, background_subtrated_866_sigma, area_866_sigma, total_uncertainty_of_background, background_subtrated_866_sigma / background_subtrated_866_area)


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
print '397 background subtracted area is {0:.2e} with unceratiny of {1:.2e} or relative uncertainty of {2:.2e}'.format(background_subtracted_397_area , background_subtracted_397_area_sigma, background_subtracted_397_area_sigma / background_subtracted_397_area)
summary_397 = 'Area 397:  {0:.1e}, relative uncertainty {2:.1e}'.format(background_subtracted_397_area , background_subtracted_397_area_sigma, background_subtracted_397_area_sigma / background_subtracted_397_area)
z = (background_subtracted_397_area / background_subtrated_866_area)
branching = z / (z + 1)
branching_error = branching * np.sqrt( (background_subtracted_397_area_sigma / background_subtracted_397_area)**2  + (background_subtrated_866_sigma / background_subtrated_866_area)**2  )/(z+1)
branching_str = u'Branching: {0:.6f} \261 {1:.6f}'.format(  branching, branching_error) 


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
pyplot.show()