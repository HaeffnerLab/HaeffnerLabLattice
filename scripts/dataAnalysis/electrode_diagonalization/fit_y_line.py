import numpy as np
import lmfit
from matplotlib import pyplot

data_array = np.array([
                #C1    C2        Ez
                [10.0,  50.0,   0.067],
                [50.0,  120.0,  0.320],
                [100.0, 200.0,  0.600],
                [200.0, 400,    1.24],
                [250.0, 480,    1.54],
                ])
data_array = data_array.transpose()
C1, C2, Ez = data_array
'''
define the function
'''
def linear_model(params, x):
    m = params['m'].value
    b = params['b'].value
    model = m * x + b
    return model
'''
define how to compare data to the function
'''
def linear_fit(params , x, y):
    model = linear_model(params, x)
    return model - y
'''
define the fitting parameters, with initial guesses. 
Here can also specify if some parameters are fixed, and the range of allowed values
'''
params0 = lmfit.Parameters()
params0.add('m', value = 1)
params0.add('b', value = 1)
params1 = lmfit.Parameters()
params1.add('m', value = 1)
params1.add('b', value = 1)
'''
run the fitting
'''
result0 = lmfit.minimize(linear_fit, params0, args = (C2, C1))
result1 = lmfit.minimize(linear_fit, params1, args = (C2, Ez))
'''
plot the result
'''
pyplot.plot(C2, C1 + result0.residual, 'r', label = 'C1 vs C2 fitted')
pyplot.plot(C2, Ez + result1.residual, 'g', label = 'Ez vs C2 fitted')
pyplot.plot(C2, C1, '*r', label = 'C1 vs C2')
pyplot.plot(C2, Ez, '*g', label = 'Ez vs C2')
pyplot.legend()
'''
print out fitting summary
'''
print 'slopes:\nm0 = {0}\nm1 = {1}'.format(params0['m'].value, params1['m'].value)
# lmfit.report_errors(params0)
# lmfit.report_errors(params1)
 

pyplot.show()