import labrad
from matplotlib import pyplot
import numpy as np
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault
date = '2013Nov22'

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
    #pyplot.plot(delays, ion1set1,'o-')
    #pyplot.plot(delays, ion1set2,'o-')
    averaged1 = (ion1set1 + ion1set2)/2
    averaged2 = (ion2set1 + ion2set2)/2
    pyplot.plot(delays, averaged1, 'o-')
    pyplot.plot(delays, averaged2, 'o-')
    pyplot.grid(True, 'both')
    pyplot.xlim(0,500)
    pyplot.ylim(0,1)
    pyplot.show()

def plot_3500():
    set1 = '1652_38'
    set2 = '1711_29'
    pyplot.subplot(111)
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
    pyplot.plot(delays, averaged1, 'o-')
    pyplot.plot(delays, averaged2, 'o-')
    pyplot.grid(True, 'both')
    pyplot.xlim(3500,4000)
    pyplot.ylim(0,1)
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
    pyplot.plot(delays, averaged1, 'o-')
    pyplot.plot(delays, averaged2, 'o-')
    pyplot.grid(True, 'both')
    pyplot.xlim(19500,19600)
    pyplot.ylim(0,1)
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
    pyplot.figure()
    pyplot.plot(delays, averaged1, 'o-')
    pyplot.plot(delays, averaged2, 'o-')
    pyplot.grid(True, 'both')
    pyplot.xlim(40000,40100)
    pyplot.ylim(0,1)
    pyplot.figure()
    pyplot.plot(delays1, ion1set1,'o-')
    pyplot.plot(delays2, ion1set2,'o-')
    pyplot.grid(True, 'both')
    pyplot.xlim(40000,40100)
    pyplot.ylim(0,1)
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
    averaged1 = (ion1set1 + ion1set2)/2
    averaged2 = (ion2set1 + ion2set2)/2
    pyplot.figure()
    pyplot.plot(delays, averaged1, 'o-')
    pyplot.plot(delays, averaged2, 'o-')
    pyplot.grid(True, 'both')
    pyplot.xlim(80000,80040)
    pyplot.ylim(0,1)
#     pyplot.figure()
#     pyplot.plot(delays1, ion1set1,'o-')
#     pyplot.plot(delays2, ion1set2,'o-')
#     pyplot.grid(True, 'both')
#     pyplot.xlim(80000,80040)
#     pyplot.ylim(0,1)
    pyplot.show()

# plot_500()
# plot_3500()
# plot_19750()
# plot_40250()
plot_80250()