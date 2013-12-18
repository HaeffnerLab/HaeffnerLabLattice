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
    pyplot.subplot(311)
    dv.cd(['','Experiments','Blue Heat ScanDelay',date,left])
    dv.open(1)
    data = dv.get().asarray
    delays,excitations = data.transpose()
    excitations = excitations / OP_reduction_left
    energy = excitation_to_energy(5)(excitations)
    pyplot.plot(delays,energy,'o-', label = '5')
    # pyplot.xlabel(r'Delay after heat $\mu s$')
#     pyplot.ylabel('Scaled Excitation')
#     pyplot.title('left ion')
#     pyplot.grid(True, 'both')
#     pyplot.ylim(0,1)
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
    pyplot.subplot(313)
    dv.cd(['','Experiments','Blue Heat ScanDelay',date,right])
    dv.open(1)
    data = dv.get().asarray
    delays,excitations = data.transpose()
    excitations = excitations / OP_reduction_right
    energy = excitation_to_energy(5)(excitations)
    pyplot.plot(delays,energy,'o-', label = '5')
#     pyplot.xlabel(r'Delay after heat $\mu s$')
#     pyplot.ylabel('Scaled Excitation')
#     pyplot.title('right ion')
#     pyplot.grid(True, 'both')
#     pyplot.ylim(0,1)

def plot_15():
    date = '2013Nov20'
    left = '1743_03'; OP_reduction_left = 0.5
#     center = '1819_08'; OP_reduction_center = 0.596
    right = '1920_13'; OP_reduction_right = 0.869
    #left, 15
    pyplot.subplot(311)
    dv.cd(['','Experiments','Blue Heat ScanDelay',date,left])
    dv.open(1)
    data = dv.get().asarray
    delays,excitations = data.transpose()
    excitations = excitations / OP_reduction_left
    energy = excitation_to_energy(15)(excitations)
    pyplot.plot(delays,energy,'o-', label = '15')
    # pyplot.xlabel(r'Delay after heat $\mu s$')
#     pyplot.ylabel('Scaled Excitation')
#     pyplot.title('left ion')
#     pyplot.grid(True, 'both')
#     pyplot.ylim(0,1)
    #center, 15
#     pyplot.subplot(312)
#     dv.cd(['','Experiments','Blue Heat ScanDelay',date,center])
#     dv.open(1)
#     data = dv.get().asarray
#     delays,excitations = data.transpose()
#     excitations = excitations / OP_reduction_center
#     print np.sort(excitations)[:4]
#     pyplot.plot(delays,excitations,'-')
#     # pyplot.xlabel(r'Delay after heat $\mu s$')
#     pyplot.ylabel('Scaled Excitation ')
#     pyplot.title('center ion')
#     pyplot.grid(True, 'both')
#     pyplot.ylim(0,1)
    #right, 15
    pyplot.subplot(313)
    dv.cd(['','Experiments','Blue Heat ScanDelay',date,right])
    dv.open(1)
    data = dv.get().asarray
    delays,excitations = data.transpose()
    excitations = excitations / OP_reduction_right
    energy = excitation_to_energy(15)(excitations)
    pyplot.plot(delays,energy,'o-', label = '15')
#     pyplot.xlabel(r'Delay after heat $\mu s$')
#     pyplot.ylabel('Scaled Excitation')
#     pyplot.title('right ion')
#     pyplot.grid(True, 'both')
#     pyplot.ylim(0,1)

def plot_25():
    date = '2013Nov20'
    left = '2035_00'; OP_reduction_left = 0.466
    center = '2116_22'; OP_reduction_center = 0.866
    right = '2139_53'; OP_reduction_right = 1.021
    #left, 25
    pyplot.subplot(311)
    dv.cd(['','Experiments','Blue Heat ScanDelay',date,left])
    dv.open(1)
    data = dv.get().asarray
    delays,excitations = data.transpose()
    excitations = excitations / OP_reduction_left
    energy = excitation_to_energy(25)(excitations)
    pyplot.plot(delays,energy,'o-', label = '25')
    # pyplot.xlabel(r'Delay after heat $\mu s$')
#     pyplot.ylabel('Scaled Excitation')
#     pyplot.title('left ion')
#     pyplot.grid(True, 'both')
#     pyplot.ylim(0,1)
    #center, 25
#     pyplot.subplot(312)
#     dv.cd(['','Experiments','Blue Heat ScanDelay',date,center])
#     dv.open(1)
#     data = dv.get().asarray
#     delays,excitations = data.transpose()
#     excitations = excitations / OP_reduction_center
#     print np.sort(excitations)[:4],np.sort(excitations)[-4:]
#     pyplot.plot(delays,excitations,'-')
#     # pyplot.xlabel(r'Delay after heat $\mu s$')
#     pyplot.ylabel('Scaled Excitation ')
#     pyplot.title('center ion')
#     pyplot.grid(True, 'both')
#     pyplot.ylim(0,1)
    #right, 25
    pyplot.subplot(313)
    dv.cd(['','Experiments','Blue Heat ScanDelay',date,right])
    dv.open(1)
    data = dv.get().asarray
    delays,excitations = data.transpose()
    excitations = excitations / OP_reduction_right
    energy = excitation_to_energy(25)(excitations)
    pyplot.plot(delays,energy,'o-', label = '25')
#     pyplot.plot(delays,excitations,'-', label = '25')
#     pyplot.xlabel(r'Delay after heat $\mu s$')
#     pyplot.ylabel('Scaled Excitation')
#     pyplot.title('right ion')
#     pyplot.grid(True, 'both')
#     pyplot.ylim(0,1)
#     pyplot.legend()
# 
# 
# 
# 
# 
# 
# 
# pyplot.tight_layout(0.5, None, None, None)
plot_5()
plot_15()
plot_25()
pyplot.show()
