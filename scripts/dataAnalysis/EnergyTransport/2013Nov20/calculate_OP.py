import labrad
from matplotlib import pyplot
import numpy as np
import lmfit
'''
comparing flops is in the form (original flop / depumped)
'''
# date = '2013Nov20'; comparing_flops = ('1545_29', '1546_39'); repetitions = 100.;#5 ions left, 0.585
# date = '2013Nov20'; comparing_flops = ('1616_14', '1617_23'); repetitions = 100.; #5 ions center, 0.612
# date = '2013Nov20'; comparing_flops = ('1645_30', '1646_40'); repetitions = 100.; #5 ions right, 0.845
# date = '2013Nov20'; comparing_flops = ('1731_49', '1738_39'); repetitions = 100.; #15 ions left, 0.727 something wrong, should use 0.5
# date = '2013Nov20'; comparing_flops = ('1815_20', '1816_30'); repetitions = 100.; #15 ions center, 0.610
# date = '2013Nov20'; comparing_flops = ('1915_31', '1916_40'); repetitions = 100.; #15 ions, right 0.881
# date = '2013Nov20'; comparing_flops = ('2010_36', '2013_05'); repetitions = 100.; #25 ions left,  0.477
# date = '2013Nov20'; comparing_flops = ('2050_54', '2052_03'); repetitions = 100.; #25 ions center, 0.846
date = '2013Nov20'; comparing_flops = ('2133_31', '2134_40'); repetitions = 100.; #25 ions 1.03

cxn = labrad.connect()
dv = cxn.data_vault
original_name, depumped_name = comparing_flops

dv.cd( ['','Experiments','Blue Heat RabiFlopping',date,depumped_name])
dv.open(1)
data = dv.get().asarray
times_pumped, probs_pumped = data.transpose()
dv.cd( ['','Experiments','RabiFlopping',date,original_name])
dv.open(1)
data = dv.get().asarray
times_original, probs_original = data.transpose()

where = times_pumped <= 900
times_pumped = times_pumped[where]
times_original = times_original[where]
probs_original = probs_original[where]
probs_pumped = probs_pumped[where]

ax1 = pyplot.subplot(211)
pyplot.plot(times_pumped, probs_pumped, 'o-', label = r'depumped')
pyplot.plot(times_pumped, probs_original, 'o-', label = r'original')
pyplot.title('Rabi Flops')
pyplot.ylabel('Excitation probability')
pyplot.ylim([0,1.0])
pyplot.legend()

# analyzed_where = (analysis_min <= times_pumped) * (times_pumped <= analysis_max)
# probs_original = probs_original[analyzed_where]
# probs_pumped = probs_pumped[analyzed_where]
sigma_original_sq = probs_original * (1 - probs_original) / repetitions
sigma_pumped_sq = probs_pumped * (1 - probs_pumped) / repetitions
times_analyzed = times_pumped#[analyzed_where]
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
print 'OP effect pumped / original = {0:.3f}'.format(params['constant'].value)

pyplot.subplot(212, sharex = ax1)
pyplot.title('Ratio')
pyplot.xlabel(u'Excitation time $\mu s$')
pyplot.errorbar(times_analyzed, ratio, sigma_ratio, fmt = '*')
pyplot.plot(times_analyzed, np.ones_like(times_analyzed)*params['constant'].value, 'r--')
pyplot.show()