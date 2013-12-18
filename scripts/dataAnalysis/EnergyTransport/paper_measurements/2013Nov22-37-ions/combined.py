import labrad
from matplotlib import pyplot
import numpy as np
from scipy.interpolate import interp1d
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault
date = '2013Nov22'


def excitation_to_energy(which_ion):
    '''
    returns a function used to convert excitations to alpha^2
    '''
    if which_ion == 0:
        filename = '37_ions_0.npy'
    elif which_ion == 1:
        filename = '37_ions_1.npy'
    else:
        raise Exception("Wrong number of ions")
    excitations, alphas = np.load(filename)
    func = interp1d(excitations, alphas**2, bounds_error = False, fill_value = np.NaN)
    return func

def get_data(date, dataset):
    dv.cd(['','Experiments','Blue Heat ScanDelay',date,dataset])
    dv.open(1)
    data = dv.get().asarray
    delays,ion1,ion2= data.transpose()
    return delays,ion1,ion2    

def plot_500():
    set1 = '1616_58'
    set2 = '1634_58'
    pyplot.subplot(111)
    delays, ion1set1,ion2set1 = get_data(date,set1)
    remove = np.argwhere(delays == 410)
    delays, ion1set2,ion2set2 = get_data(date,set2)
    ion1set1[remove] = ion1set2[remove]
    ion2set1[remove] = ion2set2[remove]
    averaged1 = (ion1set1 + ion1set2)/2
    averaged2 = (ion2set1 + ion2set2)/2
#     print averaged1.min(), averaged2.min()
#     pyplot.plot(delays, averaged1, 'o-')
#     pyplot.plot(delays, averaged2, 'o-')
#     pyplot.show()
    energy = excitation_to_energy(0)(averaged1)
    sigma =  np.sqrt(averaged1) * np.sqrt(1 - averaged1) / np.sqrt(500)
    plus_error = excitation_to_energy(0)(averaged1 + sigma) - energy
    minus_error =  excitation_to_energy(0)(averaged1 - sigma) - energy
    yerr = np.vstack((-minus_error, plus_error))
    pyplot.errorbar(delays, energy, yerr  = yerr, fmt = 'o-')
    
    energy = excitation_to_energy(1)(averaged2)
    sigma =  np.sqrt(averaged2) * np.sqrt(1 - averaged2) / np.sqrt(500)
    plus_error = excitation_to_energy(1)(averaged2 + sigma) - energy
    minus_error =  excitation_to_energy(1)(averaged2 - sigma) - energy
    minus_error[1] = averaged2[1]
    yerr = np.vstack((-minus_error, plus_error))
    pyplot.errorbar(delays, energy, yerr  = yerr, fmt = 'v-')
    
    pyplot.ylim(0,25)
    pyplot.xlim(0,550)
    ax = pyplot.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    fig = pyplot.gcf()
    fig.set_size_inches((8,6))
    pyplot.savefig('plot_500.pdf')
    pyplot.show()

def plot_3500():
    set1 = '1652_38'
    set2 = '1711_29'
    delays1, ion1set1,ion2set1 = get_data(date,set1)
    delays2, ion1set2,ion2set2 = get_data(date,set2)
    where = delays1 <=3725
    delays = delays1[where]
    ion1set1 = ion1set1[where]
    ion1set2 = ion1set2[where]
    ion2set1 = ion2set1[where]
    ion2set2 = ion2set2[where]
#     pyplot.plot(delays1, ion1set1,'o-')
#     pyplot.plot(delays2, ion1set2,'o-')
    averaged1 = (ion1set1 + ion1set2)/2
    averaged2 = (ion2set1 + ion2set2)/2
#     print averaged1.min(), averaged2.min()
#     pyplot.plot(delays, averaged1, 'o-')
#     pyplot.plot(delays, averaged2, 'o-')
    energy = excitation_to_energy(0)(averaged1)
    sigma =  np.sqrt(averaged1) * np.sqrt(1 - averaged1) / np.sqrt(500)
    plus_error = excitation_to_energy(0)(averaged1 + sigma) - energy
    minus_error =  excitation_to_energy(0)(averaged1 - sigma) - energy
    yerr = np.vstack((-minus_error, plus_error))
    pyplot.errorbar(delays, energy, yerr  = yerr, fmt = 'o-')
    
    energy = excitation_to_energy(1)(averaged2)
    sigma =  np.sqrt(averaged2) * np.sqrt(1 - averaged2) / np.sqrt(500)
    plus_error = excitation_to_energy(1)(averaged2 + sigma) - energy
    minus_error =  excitation_to_energy(1)(averaged2 - sigma) - energy
    yerr = np.vstack((-minus_error, plus_error))
    pyplot.errorbar(delays, energy, yerr  = yerr, fmt = 'v-')
#     pyplot.grid(True, 'both')
    ax = pyplot.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.yaxis.set_major_locator(pyplot.NullLocator())
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks([3500, 3600, 3700])
    pyplot.xlim(3450,3775)
    pyplot.ylim(0,25)
    fig = pyplot.gcf()
    fig.set_size_inches((8 * 325.0 / 550,6))
    pyplot.savefig('plot_3500.pdf')
    pyplot.show()
    
def plot_19750():
    set1 = '1744_35'
    set2 = '1751_50'
    pyplot.subplot(111)
    delays1, ion1set1,ion2set1 = get_data(date,set1)
    delays2, ion1set2,ion2set2 = get_data(date,set2)
    delays = delays1
    delays2 = delays2[:-1]
    ion1set2 = ion1set2[:-1]
    ion2set2 = ion2set2[:-1]
#     pyplot.plot(delays1, ion2set1,'o-')
#     pyplot.plot(delays2, ion2set2,'o-')
    averaged1 = (ion1set1 + ion1set2)/2
    averaged2 = (ion2set1 + ion2set2)/2
#     print averaged1.min(), averaged2.min()
#     pyplot.plot(delays, averaged1, 'o-')
#     pyplot.plot(delays, averaged2, 'o-')
    energy = excitation_to_energy(0)(averaged1)
    sigma =  np.sqrt(averaged1) * np.sqrt(1 - averaged1) / np.sqrt(500)
    plus_error = excitation_to_energy(0)(averaged1 + sigma) - energy
    minus_error =  excitation_to_energy(0)(averaged1 - sigma) - energy
    yerr = np.vstack((-minus_error, plus_error))
    pyplot.errorbar(delays, energy, yerr  = yerr, fmt = 'o-')
    
    energy = excitation_to_energy(1)(averaged2)
    sigma =  np.sqrt(averaged2) * np.sqrt(1 - averaged2) / np.sqrt(500)
    plus_error = excitation_to_energy(1)(averaged2 + sigma) - energy
    minus_error =  excitation_to_energy(1)(averaged2 - sigma) - energy
    minus_error[1] = averaged2[1]
    yerr = np.vstack((-minus_error, plus_error))
    pyplot.errorbar(delays, energy, yerr  = yerr, fmt = 'v-')
#     pyplot.grid(True, 'both')
    pyplot.xlim(19450,19650)
    pyplot.ylim(0,25)
    ax = pyplot.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.yaxis.set_major_locator(pyplot.NullLocator())
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks([19500, 19600])
    fig = pyplot.gcf()
    fig.set_size_inches((8 * 200.0 / 550,6))
    pyplot.savefig('plot_19750.pdf')
    pyplot.show()
    pyplot.show()

def plot_40250():
    set1 = '1759_45'
    set2 = '1811_54'
    delays1, ion1set1,ion2set1 = get_data(date,set1)
    delays2, ion1set2,ion2set2 = get_data(date,set2)
    delays = delays1
    delays2 = delays2[:-3]
    ion1set2 = ion1set2[:-3]
    ion2set2 = ion2set2[:-3]
    averaged1 = (ion1set1 + ion1set2)/2
    averaged2 = (ion2set1 + ion2set2)/2
#     print averaged1.min(), averaged2.min()
    pyplot.figure()
#     pyplot.plot(delays, averaged1, 'o-')
#     pyplot.plot(delays, averaged2, 'o-')
    energy = excitation_to_energy(0)(averaged1)
    sigma =  np.sqrt(averaged1) * np.sqrt(1 - averaged1) / np.sqrt(500)
    plus_error = excitation_to_energy(0)(averaged1 + sigma) - energy
    minus_error =  excitation_to_energy(0)(averaged1 - sigma) - energy
    yerr = np.vstack((-minus_error, plus_error))
    pyplot.errorbar(delays, energy, yerr  = yerr, fmt = 'o-')
    
    energy = excitation_to_energy(1)(averaged2)
    sigma =  np.sqrt(averaged2) * np.sqrt(1 - averaged2) / np.sqrt(500)
    plus_error = excitation_to_energy(1)(averaged2 + sigma) - energy
    minus_error =  excitation_to_energy(1)(averaged2 - sigma) - energy
    minus_error[1] = averaged2[1]
    yerr = np.vstack((-minus_error, plus_error))
    pyplot.errorbar(delays, energy, yerr  = yerr, fmt = 'v-')
#     pyplot.grid(True, 'both')
    pyplot.xlim(39950,40150)
    pyplot.ylim(0,25)
    ax = pyplot.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.yaxis.set_major_locator(pyplot.NullLocator())
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks([40000, 40100])
    fig = pyplot.gcf()
    fig.set_size_inches((8 * 200.0 / 550,6))
    pyplot.savefig('plot_40250.pdf')
    pyplot.show()
    pyplot.figure()
#     pyplot.plot(delays1, ion1set1,'o-')
#     pyplot.plot(delays2, ion1set2,'o-')
    pyplot.plot(delays, excitation_to_energy(0)(ion1set1), 'o-')
    pyplot.plot(delays, excitation_to_energy(1)(ion1set2), 'v-')
    pyplot.grid(True, 'both')
    pyplot.xlim(40000,40100)
    pyplot.ylim(0,25)
    pyplot.show()
    
def plot_80250():
    set1 = '1823_27'
    set2 = '1842_43'
    delays1, ion1set1,ion2set1 = get_data(date,set1)
    delays2, ion1set2,ion2set2 = get_data(date,set2)
    delays = delays2
    delays1 = delays1[:-1]
    ion1set1 = ion1set1[:-1]
    ion2set1 = ion2set1[:-1]
    #removing points where lost ion
    where = delays1 <=80030
    delays = delays1[where]
    ion1set1 = ion1set1[where]
    ion1set2 = ion1set2[where]
    ion2set1 = ion2set1[where]
    ion2set2 = ion2set2[where]
    
    averaged1 = (ion1set1 + ion1set2)/2
    averaged2 = (ion2set1 + ion2set2)/2
#     print averaged1.min(), averaged2.min()
    pyplot.figure()
#     pyplot.plot(delays, averaged1, 'o-')
#     pyplot.plot(delays, averaged2, 'o-')
    energy = excitation_to_energy(0)(averaged1)
    sigma =  np.sqrt(averaged1) * np.sqrt(1 - averaged1) / np.sqrt(500)
    plus_error = excitation_to_energy(0)(averaged1 + sigma) - energy
    minus_error =  excitation_to_energy(0)(averaged1 - sigma) - energy
    yerr = np.vstack((-minus_error, plus_error))
    pyplot.errorbar(delays, energy, yerr  = yerr, fmt = 'o-', label = 'rightmost ion')
    
    energy = excitation_to_energy(1)(averaged2)
    sigma =  np.sqrt(averaged2) * np.sqrt(1 - averaged2) / np.sqrt(500)
    plus_error = excitation_to_energy(1)(averaged2 + sigma) - energy
    minus_error =  excitation_to_energy(1)(averaged2 - sigma) - energy
    minus_error[1] = averaged2[1]
    yerr = np.vstack((-minus_error, plus_error))
    pyplot.errorbar(delays, energy, yerr  = yerr, fmt = 'v-', label = 'ion second from right')
#     pyplot.grid(True, 'both')
    pyplot.xlim(79850,80150)
#     pyplot.ylim(0,1)
#     pyplot.figure()
#     pyplot.plot(delays1, ion1set1,'o-')
#     pyplot.plot(delays2, ion1set2,'o-')
#     pyplot.grid(True, 'both')
#     pyplot.xlim(80000,80040)
    pyplot.ylim(0,25)
    ax = pyplot.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.yaxis.set_major_locator(pyplot.NullLocator())
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks([80000, 80100])
    fig = pyplot.gcf()
    fig.set_size_inches((8 * 300.0 / 550,6))
    pyplot.legend()
    pyplot.savefig('plot_80250.pdf')
    pyplot.show()

# plot_500()
# plot_3500()
# plot_19750()
# plot_40250()
plot_80250()