from __future__ import division
import matplotlib

from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import labrad
'''
this analyzes the tomography experiment on April 02, 2013 where we compare (a) tomography at the dephasing time with no dephasing
and (b) tomography at the dephasing time after the dephasing. The results are the same, showing no coherence
(as it must be due to frequency switching) and therefore we are dephasing in the right basis.
'''
trials = 100
date = '2013Apr02'
#before dephasing
#folders = ['2258_22','2258_28','2258_34','2258_41','2258_47','2258_53','2258_59','2259_06','2259_12','2259_18']
#after dephasing
folders = ['2259_58','2300_04','2300_10','2300_16','2300_23','2300_29','2300_35','2301_25','2301_31','2301_37']
results = np.zeros((len(folders), 3))
cxn = labrad.connect()
dv = cxn.data_vault
for i,folder in enumerate(folders):
    dv.cd(['', 'Experiments','RamseyDephaseTomography', date, folder])
    dv.open(1)
    measurement = dv.get().asarray
    results[i] = measurement.transpose()[1]
p1,p2,p3 = np.average(results, axis = 0)

z = p1
y = p2 - 1/2
x = 1/2 - p3

density_matrx = np.array([[z, x + 1j*y],[x - 1j*y, 1 - z]])

absol=np.abs(density_matrx)
fig = pyplot.figure()

labels = [r'$|e\rangle$',r'$|g\rangle$']
#first plot
ax = fig.add_subplot(111, projection = '3d')



ax.set_zticks((0.0,0.5,1.0))
ax.set_zticklabels([0,0.5,1], fontsize = 22)
#ax.tick_params(axis='z', labelsize=22)
#cl = pyplot.getp(cax, 'ymajorticklabels') 
#pyplot.setp(cl, fontsize=22)
#next subplot
#ax = fig.add_subplot(122, projection = '3d')
#ax.set_title('Imaginary', fontsize = 30)
#q.matrix_histogram(imag, limits = zlim, fig = fig, ax = ax, colorbar = False)
#ax.set_xticklabels(labels, fontsize = 22)
#ax.set_yticklabels(labels, fontsize = 22)
#ax.tick_params(axis='z', labelsize=22)
#cax, kw = matplotlib.colorbar.make_axes(ax, shrink=.75, pad=.0)
#cb1 = matplotlib.colorbar.ColorbarBase(cax, norm = norm)
#cl = pyplot.getp(cax, 'ymajorticklabels') 
#pyplot.setp(cl, fontsize=22)


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

xpos, ypos = np.meshgrid(np.arange(2), np.arange(2))
xpos = 0.5 * xpos.flatten()
ypos = 0.5 * ypos.flatten()
zpos = np.zeros(4)
dx = 0.4 * np.ones_like(zpos)
dy = dx.copy()
dz = absol.flatten()

ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color='#FFCC00', zsort='average')
ax.set_xticklabels(labels, fontsize = 30)
ax.set_yticklabels(labels, fontsize = 30)
ax.xaxis.set_ticks([0.25,0.75])
ax.yaxis.set_ticks([0.25,0.75])
ax.disable_mouse_rotation()
#ax.grid(True, linestyle = '--', fillstyle = None)
#ax.set_xlim([0,2])
#ax.set_ylim([0,2])
ax.set_zlim([0,1])
ax.view_init(35, 315)
pyplot.savefig('denisty_matrix.pdf')
pyplot.show()
