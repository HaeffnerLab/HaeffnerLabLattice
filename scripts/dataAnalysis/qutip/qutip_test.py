from matplotlib import pyplot
import qutip as q
import numpy as np

measurement = [1.0, 0.5, 0.5]

p1, p2, p3 = measurement
density_matrx = np.array([[1-p1, p3 - .5 + 1.j * (p2-.5)],[p3 - .5 - 1.j * (p2-.5), p1]])
real = np.real(density_matrx)
imag = np.imag(density_matrx)

fig = pyplot.figure()
ax = fig.add_subplot(131, projection = '3d')
q.matrix_histogram(real,  title = 'Real', limits = [-1,1], fig = fig, ax = ax)
ax = fig.add_subplot(132, projection = '3d')
q.matrix_histogram(imag, title = 'Imaginary', limits = [-1,1], fig = fig, ax = ax)
ax = fig.add_subplot(133)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

def errorBarSimple(trials, prob):
    #look at wiki http://en.wikipedia.org/wiki/Checking_whether_a_coin_is_fair
    '''returns 1 sigma error bar on each side i.e 1 sigma interval is val - err < val + err'''
    Z = 1.0
    s = np.sqrt(prob * (1.0 - prob) / float(trials))
    err = Z * s
    return err

err = errorBarSimple
trials = 100

error_matrix = np.array(
                        [
                         [err(trials, p1), err(trials,p3) + 1.j * err(trials, p2)],
                         [err(trials,p3) - 1.j * err(trials,p2), err(trials,p1)]
                         ]
                        )

ax.annotate("Measurement", xy=(0.2, 0.8), fontsize = 20, xycoords="axes fraction")
ax.annotate(density_matrx, xy=(0.2, 0.7), fontsize = 20, xycoords="axes fraction")
ax.annotate(" 'Error Bar' ", xy=(0.2, 0.6), fontsize = 20, xycoords="axes fraction")
ax.annotate(error_matrix, xy=(0.2, 0.5), fontsize = 20, xycoords="axes fraction")
pyplot.show()