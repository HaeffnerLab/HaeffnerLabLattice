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
    func = interp1d(excitations, alphas**2, bounds_error = False, fill_value = np.NaN)
    return func

def plot_5():
    date = '2013Nov20'
    right = '1649_34'; OP_reduction_right = 0.845
    dv.cd(['','Experiments','Blue Heat ScanDelay',date,right])
    dv.open(1)
    data = dv.get().asarray
    delays,excitations = data.transpose()
    excitations = excitations / OP_reduction_right
    energy = excitation_to_energy(5)(excitations)
    sigma =  np.sqrt(excitations) * np.sqrt(1 - excitations) / np.sqrt(500)
    plus_error = excitation_to_energy(5)(excitations + sigma) - energy
    minus_error =  excitation_to_energy(5)(excitations - sigma) - energy
    minus_error[0] = energy[0]
    yerr = np.vstack((-minus_error, plus_error))
    pyplot.errorbar(delays, energy, yerr  = yerr, fmt = 'bo-', label = '5 ions')
    pyplot.ylim(0,90)
    ax = pyplot.gca()
    ax.xaxis.set_ticklabels([])
    pyplot.legend()

def plot_15():
    date = '2013Nov20'
    right = '1920_13'; OP_reduction_right = 0.881
    dv.cd(['','Experiments','Blue Heat ScanDelay',date,right])
    dv.open(1)
    data = dv.get().asarray
    delays,excitations = data.transpose()
    excitations = excitations / OP_reduction_right
    energy = excitation_to_energy(15)(excitations)
    sigma =  np.sqrt(excitations) * np.sqrt(1 - excitations) / np.sqrt(500)
    plus_error = excitation_to_energy(15)(excitations + sigma) - energy
    minus_error =  excitation_to_energy(15)(excitations - sigma) - energy
    yerr = np.vstack((-minus_error, plus_error))
    pyplot.errorbar(delays, energy, yerr  = yerr, fmt = 'go-', label = '15 ions')
    pyplot.ylim(0,90)
    ax = pyplot.gca()
    ax.xaxis.set_ticklabels([])
    pyplot.legend()
    
def plot_25():
    date = '2013Nov20'
    right = '2139_53'; OP_reduction_right = 1.03
    #right, 25
    dv.cd(['','Experiments','Blue Heat ScanDelay',date,right])
    dv.open(1)
    data = dv.get().asarray
    delays,excitations = data.transpose()
    excitations = excitations / OP_reduction_right
    energy = excitation_to_energy(25)(excitations)
    sigma =  np.sqrt(excitations) * np.sqrt(1 - excitations) / np.sqrt(500)
    plus_error = excitation_to_energy(25)(excitations + sigma) - energy
    minus_error =  excitation_to_energy(25)(excitations - sigma) - energy
    yerr = np.vstack((-minus_error, plus_error))
    pyplot.errorbar(delays, energy, yerr  = yerr, fmt = 'ro-', label = '25 ions')
    pyplot.ylim(0,90)
    pyplot.legend()

# plot_5(); save_name = 'right_ion_combined_5'
# plot_15(); save_name = 'right_ion_combined_15'
# plot_25(); save_name = 'right_ion_combined_25'
save = True

if not save:
    print 'NOT SAVING'
else:
    fig = pyplot.gcf()
    fig.set_size_inches(12,6)
    pyplot.savefig('{0}.pdf'.format(save_name))
pyplot.show()
