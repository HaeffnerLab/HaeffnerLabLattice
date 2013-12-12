import labrad
from matplotlib import pyplot
import numpy as np
from scipy.interpolate import interp1d
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

def excitation_to_energy(which_conversion):
    '''
    returns a function used to convert excitations to alpha^2
    '''
    if which_conversion == 5:
        filename = '5_ions_leftandright.npy'
    elif which_conversion == 15:
        filename = '15_ions_leftandright.npy'
    elif which_conversion == 25:
        filename = '25_ions_leftandright.npy'
    else:
        raise Exception("Wrong number of ions")
    excitations, alphas = np.load(filename)
    func = interp1d(excitations, alphas**2)
    return func

def plot_5():
    date = '2013Nov20'
    left = '1558_38'; OP_reduction_left = 0.585
    center = '1618_53'; OP_reduction_center = 0.612
    right = '1649_34'; OP_reduction_right = 0.845
    #left, 5
    pyplot.subplot(121)
    dv.cd(['','Experiments','Blue Heat ScanDelay',date,left])
    dv.open(1)
    data = dv.get().asarray
    delays,excitations = data.transpose()
    excitations = excitations / OP_reduction_left
    energy = excitation_to_energy(5)(excitations)
    pyplot.plot(delays,energy,'o-', label = '5')
    ax = pyplot.gca()
    ax.xaxis.set_ticklabels([])
#     ax.yaxis.set_ticks_position('left')
    # pyplot.xlabel(r'Delay after heat $\mu s$')
#     pyplot.ylabel('Scaled Excitation')
#     pyplot.title('left ion')
#     pyplot.grid(True, 'both')
    pyplot.xlim(-10, 610)
    pyplot.ylim(0,120)
    #center, 5
#     pyplot.subplot(312)
#     dv.cd(['','Experiments','Blue Heat ScanDelay',date,center])
#     dv.open(1)
#     data = dv.get().asarray
#     delays,excitations = data.transpose()
#     excitations = excitations / OP_reduction_center
#     # pyplot.xlabel(r'Delay after heat $\mu s$')
#     pyplot.ylabel('Scaled Excitation ')
#     pyplot.title('center ion')
#     pyplot.grid(True, 'both')
#     pyplot.ylim(0,1)
#     #right, 5
    pyplot.subplot(122)
    dv.cd(['','Experiments','Blue Heat ScanDelay',date,right])
    dv.open(1)
    data = dv.get().asarray
    delays,excitations = data.transpose()
    excitations = excitations / OP_reduction_right
    energy = excitation_to_energy(5)(excitations)
    pyplot.plot(delays,energy,'o-', label = '5 ions')
    pyplot.xlim(-10, 610)
    pyplot.ylim(0,120)
    ax = pyplot.gca()
    ax.yaxis.set_ticklabels([])
    ax.xaxis.set_ticklabels([])
#     ax.yaxis.set_major_locator(pyplot.NullLocator())
#     pyplot.xlabel(r'Delay after heat $\mu s$')
#     pyplot.ylabel('Scaled Excitation')
#     pyplot.title('right ion')
#     pyplot.grid(True, 'both')
#     pyplot.ylim(0,1)


plot_5()
pyplot.tight_layout()
# plot_15()
# plot_25()
pyplot.subplots_adjust(wspace = 0)
fig = pyplot.gcf()
fig.set_size_inches(19.2,5.4)
pyplot.savefig('comparison_theory_top.pdf')
pyplot.show()
