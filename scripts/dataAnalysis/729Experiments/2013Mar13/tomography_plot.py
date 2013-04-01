from __future__ import division
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
import qutip as q
import numpy as np
import labrad
cxn = labrad.connect()
dv = cxn.data_vault

'''
this plots the result of 2126_42, which is when we drove a sideband pulse for pi/2 and then did tomography.
'''
folder = '2126_42'
dv.cd(['', 'Experiments','RamseyDephaseCheckCoherenceTomography', '2013Mar13'])
dv.cd(folder)
dv.open(1)
trials = dv.get_parameter('Tomography.repeat_each_measurement')
measurement = dv.get().asarray
p1, p2, p3 = measurement.transpose()[1]
z = p1
y = p2 - 1/2
x = 1/2 - p3

density_matrx = np.array([[z, x + 1j*y],[x - 1j*y, 1 - z]])

real = np.real(density_matrx)
imag = np.imag(density_matrx)

fig = pyplot.figure()
labels = ['|D>','|S>']
ax = fig.add_subplot(121, projection = '3d')
ax.set_title('Real', fontsize = 30)
q.matrix_histogram(real,  limits = [-1,1], fig = fig, ax = ax, xlabels = labels, ylabels = labels)
ax = fig.add_subplot(122, projection = '3d')
ax.set_title('Imaginary', fontsize = 30)
q.matrix_histogram(imag, limits = [-1,1], fig = fig, ax = ax, xlabels = labels, ylabels = labels)

#ax = fig.add_subplot(133)
#ax.get_xaxis().set_visible(False)
#ax.get_yaxis().set_visible(False)

#def errorBarSimple(trials, prob):
#    #look at wiki http://en.wikipedia.org/wiki/Checking_whether_a_coin_is_fair
#    '''returns 1 sigma error bar on each side i.e 1 sigma interval is val - err < val + err'''
#    Z = 1.0
#    s = np.sqrt(prob * (1.0 - prob) / float(trials))
#    err = Z * s
#    return err
#
#err = errorBarSimple
#
#
#error_matrix = np.array(
#                        [
#                         [err(trials, p1), err(trials,p3) + 1.j * err(trials, p2)],
#                         [err(trials,p3) - 1.j * err(trials,p2), err(trials,p1)]
#                         ]
#                        )
#error_matrix = np.round(error_matrix, 2)

#ax.annotate("Measurement", xy=(0.2, 0.8), fontsize = 20, xycoords="axes fraction")
#ax.annotate(density_matrx, xy=(0.2, 0.7), fontsize = 20, xycoords="axes fraction")
#ax.annotate(" 'Error Bar' ", xy=(0.2, 0.6), fontsize = 20, xycoords="axes fraction")
#ax.annotate(error_matrix, xy=(0.2, 0.5), fontsize = 20, xycoords="axes fraction")
pyplot.show()