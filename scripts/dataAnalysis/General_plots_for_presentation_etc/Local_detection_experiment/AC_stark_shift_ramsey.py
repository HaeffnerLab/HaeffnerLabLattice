import labrad
from matplotlib import pyplot
import lmfit
import numpy as np
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

dv.cd(['','Experiments','RamseyDephaseScanDuration','2013Mar15','2142_08'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]
figure = pyplot.figure()
figure.clf()
pyplot.plot(x, y,'o')

# pyplot.title('AC Stark Shift', fontsize = 40)
pyplot.ylim([0,1])
# pyplot.xlabel(r'Interaction Time ( $\mu s$ )', fontsize = 32)
# pyplot.ylabel('Excitation percentage', fontsize = 32)
pyplot.tick_params('both', labelsize = 20)

'''
define the function
'''
def sin_model(params, x):
    contrast = params['contrast'].value
    offset = params['offset'].value
    period = params['period'].value
    phase = params['phase'].value
    model =  offset + contrast/2. * np.sin( 2 * np.pi * x / period + phase)
    return model
'''
define how to compare data to the function
'''
def fit(params , x, data):
    model = sin_model(params, x)
    return model - data

params = lmfit.Parameters()
params.add('contrast', value = 0.8, max = 1.0)
params.add('offset', value = 0)
params.add('period', value = 25, min = 0.0)
params.add('phase', value = 0)
'''
run the fitting
'''
result = lmfit.minimize(fit, params, args = (x, y))
'''
plot the result
'''
fit_values  = y + result.residual
x_sample = np.linspace(x.min(), x.max(), 1000)
pyplot.plot(x_sample, sin_model(params, x_sample), 'r', label = 'Sine Fit')
'''
print out fitting summary
'''
lmfit.report_errors(params)

pyplot.legend()
pyplot.tight_layout()
figure.set_size_inches(12,6)
pyplot.xlim(0,40)
pyplot.savefig("AC_Stark_shift.pdf", dpi = 600)
pyplot.show()
