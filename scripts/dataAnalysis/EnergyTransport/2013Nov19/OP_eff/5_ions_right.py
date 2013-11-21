import labrad
from matplotlib import pyplot
import numpy as np
import lmfit
#comparing flops is in the form (original flop / depumped)
date = '2013Nov18'; comparing_flops = ('1355_58', '1356_59'); repetitions = 100.;
analysis_min,analysis_max = (0.1, 20) #microseconds

cxn = labrad.connect()
dv = cxn.data_vault
original_name, depumped_name = comparing_flops

dv.cd( ['','Experiments','Blue Heat RabiFlopping',date,depumped_name])
dv.open(1)
data = dv.get().asarray
times_pumped, a,b,c,d,probs_pumped = data.transpose()
dv.cd( ['','Experiments','RabiFlopping',date,original_name])
dv.open(1)
data = dv.get().asarray
times_original, a,b,c,d,probs_original = data.transpose()

#quick hack to have the same number of points
probs_original = probs_original[:-4]
print probs_original.size
print probs_pumped.size

ax1 = pyplot.subplot(211)
pyplot.plot(times_pumped, probs_pumped, 'o-', label = r'depumped')
pyplot.plot(times_pumped, probs_original, 'o-', label = r'original')
pyplot.title('Rabi Flops')
pyplot.ylabel('Excitation probability')
pyplot.ylim([0,1.0])
pyplot.legend()

analyzed_where = (analysis_min <= times_pumped) * (times_pumped <= analysis_max)
probs_original = probs_original[analyzed_where]
probs_pumped = probs_pumped[analyzed_where]
sigma_original_sq = probs_original * (1 - probs_original) / repetitions
sigma_pumped_sq = probs_pumped * (1 - probs_pumped) / repetitions
times_analyzed = times_pumped[analyzed_where]
ratio = probs_pumped/probs_original
sigma_ratio = ratio * np.sqrt(sigma_original_sq / probs_original**2 + sigma_pumped_sq / probs_pumped**2)

'''
define the function
'''
def constant_model(params, x):
    constant = params['constant'].value
    return constant * np.ones_like(x)
'''
define how to compare data to the function
'''
def constant_fit(params , x, data):
    model = constant_model(params, x)
    return (model - data) / sigma_ratio

params = lmfit.Parameters()
params.add('constant', value = 0.9, max = 2.0)
result = lmfit.minimize(constant_fit, params, args = (times_analyzed, ratio))
print 'OP reduction', params['constant'].value

pyplot.subplot(212, sharex = ax1)
pyplot.title('Ratio')
pyplot.xlabel(u'Excitation time $\mu s$')
pyplot.errorbar(times_analyzed, ratio, sigma_ratio, fmt = '*')
pyplot.plot(times_analyzed, np.ones_like(times_analyzed)*params['constant'].value, 'r--')



pyplot.show()