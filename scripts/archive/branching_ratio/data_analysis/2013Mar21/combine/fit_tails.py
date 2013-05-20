from __future__ import division
import numpy as np
import matplotlib
#from constants import constants as c

from matplotlib import pyplot
import lmfit
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


def exp_model(params, x):
    amplitude = params['amplitude'].value
    time_constant = params['time_constant'].value
    background_level = params['background_level'].value
    offset = x.min()
    model =  background_level + amplitude * np.exp( - (x - offset) / time_constant)
    return model

def exponent_fit(params , x, data):
    model = exp_model(params, x)
    return model - data

fit_domain = (90,100)
#fit_domain = (30,40)
fit_where = np.where((fit_domain[0] <= bins) * (bins <= fit_domain[1]))
fit_bins,fit_hist = bins[fit_where], hist[fit_where]

params = lmfit.Parameters()
params.add('amplitude', value = 500)
params.add('time_constant', value = 2.5)
params.add('background_level', value = 51)

result = lmfit.minimize(exponent_fit, params, args = (fit_bins, fit_hist), **{'ftol':1e-30, 'xtol':1e-30} )
final  = fit_hist + result.residual

predicted_level = params['background_level'].value

lmfit.report_errors(params)
correction = predicted_level - 0.935661264542
print correction, params['background_level'].stderr

pyplot.plot(bins, hist, 'x', markersize = 1)
pyplot.plot(fit_bins, final, 'r')
pyplot.show()