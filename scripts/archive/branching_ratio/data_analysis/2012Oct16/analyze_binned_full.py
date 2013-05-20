import numpy as np
import matplotlib

from matplotlib import pyplot
from scipy.optimize import curve_fit

binned_file = '00001 - Timetags 2012Oct16_2036_59_binned.npy'
f = np.load(binned_file)
bins = f[:,0]
hist = f[:,1]
bins = bins*1e6 #time now in mus
#find the background level
background_domain = (0.0, 20.0)
background_where = np.where((background_domain[0] <= bins) * (bins <= background_domain[1]))
background_bins,background_counts = bins[background_where], hist[background_where]
background_total = background_counts.sum()
background_level = background_total / float(background_bins.size)
background_level_sigma = np.sqrt(np.sum(background_total)) /  float(background_bins.size)
print 'Calculated background level to be {0:.2f} with sigma of {1:.2f}, relative uncertainty {2:.2e}'.format(background_level, background_level_sigma, background_level_sigma / background_level)

#calculate the area of 866 peak
peak_866 = (61.0, 65.0)
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

completed_sequences = 360e6 * 0.93 
collection_efficiency = background_subtrated_866_area / completed_sequences
collection_str = 'Collection efficiency {:.1e}'.format(collection_efficiency)
print collection_str

#after light on, fit the exponential
domain_397 = (23.0, 35.0)
domain_397_where = np.where((domain_397[0] <= bins) * (bins <= domain_397[1]))
domain_397_bins,domain_397_counts = bins[domain_397_where], hist[domain_397_where]

x,y = domain_397_bins,domain_397_counts
err = np.sqrt(domain_397_counts)
n = len(x) # the number of data points

def f(x , A, time_constant, background_397):
    offset = x.min()
    y =  background_level + background_397 + A * np.exp( - (x - offset) / time_constant)
    return y
    
p0 = [5000, 10, 5000] # initial values of parameters
p, covm = curve_fit(f, x, y, p0, err) # do the fit
A,tau,background_397 = p
#print 'red fit gives tau:{0:.2e}, background_397:{1:.2e}'.format(tau, background_397)

#after light on, fit the exponential
domain_fall = (38.0, 45.0)
domain_fall_where = np.where((domain_fall[0] <= bins) * (bins <= domain_fall[1]))
domain_fall_bins,domain_fall_counts = bins[domain_fall_where], hist[domain_fall_where]
err = np.sqrt(domain_fall_counts)

def slope(x , t1, t2):
    y = np.zeros_like(x)
    before = np.where(x < t1)
    after = np.where(x > t2)
    during = np.where((x >= t1) * (x <= t2))
    
    y[before] = background_397 + background_level
    y[after] = background_level
    x_during = x[during]
    y[during] =  background_397 + background_level - (background_397 ) / (t2 - t1) * (x_during - t1 ) 
    return y

p0 = [41.0, 42.0] # initial values of parameters
p, covm = curve_fit(slope, domain_fall_bins, domain_fall_counts, p0, err) # do the fit
t1, t2 = p
bin_size = bins[1] - bins[0]
t1 = t1 - t1 % bin_size
t2 = t2 - t2 % bin_size



def rise(x, t_start, B):
    y = np.zeros_like(x)
    before = np.where(x < t_start)
    after = np.where(x >= t_start)
    x_after = x[after]
    y[before] = background_level
    y[after] = B * (x_after -  t_start) + background_level
    return y

rise_domain = (20.5, 22.0)
rise_domain_where = np.where((rise_domain[0] <= bins) * (bins <= rise_domain[1]))
rise_bins,rise_counts =  bins[rise_domain_where], hist[rise_domain_where]
err = np.sqrt(rise_counts)
p0 = [21.7, 100.0]
p, covm = curve_fit(rise, rise_bins, rise_counts, p0, err)#do the fit
t_start,B = p
t_start = t_start - t_start % bin_size

#computing the area of the 397 peak
peak_397_domain = (15.75, 33.0)
peak_397_where = np.where((peak_397_domain[0] <= bins) * (bins <= peak_397_domain[1]))
peak_397_bins,peak_397_counts = bins[peak_397_where], hist[peak_397_where]

peak_397_area = np.sum(peak_397_counts)
peak_397_area_sigma = np.sqrt(peak_397_area)

background_397_area = peak_397_bins.size * background_level + .5 * (t2 - t1) / bin_size *  background_397 + (peak_397_domain[1] - t_start -  (t2 - t1)) / bin_size * background_397
background_397_area_sigma = np.sqrt(background_397_area)
background_subtracted_397_area = peak_397_area - background_397_area 
background_subtracted_397_area_sigma = np.sqrt(peak_397_area_sigma**2 + background_397_area_sigma**2)

print '397 background subtracted area is {0:.2e} with unceratiny of {1:.2e} or relative uncertainty of {2:.2e}'.format(background_subtracted_397_area , background_subtracted_397_area_sigma, background_subtracted_397_area_sigma / background_subtracted_397_area)
summary_397 = 'Area 397:  {0:.1e}, relative uncertainty {2:.1e}'.format(background_subtracted_397_area , background_subtracted_397_area_sigma, background_subtracted_397_area_sigma / background_subtracted_397_area)
z = (background_subtracted_397_area / background_subtrated_866_area)
branching = z / (z + 1)
branching_error = branching * np.sqrt( (background_subtracted_397_area_sigma / background_subtracted_397_area)**2  + (background_subtrated_866_sigma / background_subtrated_866_area)**2  )
branching_str = u'Branching: {0:.3f} \261 {1:.3f}'.format(  branching, branching_error) 

pyplot.plot(domain_fall_bins, slope(domain_fall_bins, t1, t2), 'r', linewidth=1.0)
pyplot.plot(x, f(x, A, tau, background_397), 'r', linewidth=1.0)
pyplot.plot(background_bins, background_level * np.ones_like(background_bins), 'r', linewidth=1.0)
pyplot.plot(rise_bins, rise(rise_bins, t_start, B), 'r', linewidth=1.0)
pyplot.plot(bins, hist, '.k', markersize=0.7)

pyplot.annotate(branching_str, xy=(0.55, 0.80), xycoords='axes fraction')
pyplot.annotate(collection_str, xy=(0.55, 0.85), xycoords='axes fraction')
pyplot.annotate(summary_866, xy=(0.55, 0.95), xycoords='axes fraction')
pyplot.annotate(summary_397, xy=(0.55, 0.90), xycoords='axes fraction')

pyplot.ylim(ymin = 0)
pyplot.title('Branching Ratio ' + binned_file)
pyplot.xlabel(u'Time \265s')
pyplot.ylabel('Photons per bin of 10 ns')
pyplot.show()