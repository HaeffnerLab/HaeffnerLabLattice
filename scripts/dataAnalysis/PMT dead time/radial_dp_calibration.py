import numpy as np
from labrad.units import WithUnit as U
from matplotlib import pyplot
#220 MHz
calibration = [
#               (-3.0, U(10, 'uW')), 
               (-6.0, U(9.45, 'uW')),
               (-9.0, U(6.30, 'uW')),
               (-12.0, U(2.35, 'uW')),
               (-15.0, U(555, 'nW')),
               (-18.0, U(120, 'nW')),
               (-21.0, U(24, 'nW')),
               (-24.0, U(5, 'nW')),
#               (-27.0, U(1, 'nW')),
                   ]

#measuring total count for 10 seconds, averaged to count per 10ms
power_counts = [
                (-6.0, 11859.125),
                (-9.0, 7837.775),
                (-12.0, 2938.582),
                (-15.0, 677.15),
                (-18.0, 150.931),
                (-21.0, 29.257),
                (-24.0, 5.948),
#                (-27.0, 1.415),
                ]

x_values = np.array(power_counts).transpose()[0]
counts = np.array(power_counts).transpose()[1] * 100 #now in counts per sec
powers = np.array([calib[1]['nW'] for calib in calibration])
y_values = counts / powers
y_values /= y_values.min()
pyplot.figure()
pyplot.plot(counts / 1000.0, y_values, 'x')
pyplot.xlabel("KiloCounts / Sec")
pyplot.ylabel("Deviation from linear count rate")
pyplot.show()                                          