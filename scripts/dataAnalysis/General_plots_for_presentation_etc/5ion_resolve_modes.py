import labrad
import matplotlib as mpl
from matplotlib import pyplot


def mpl_for_saving():
    mpl.rc('xtick', labelsize = 'x-large')
    mpl.rc('ytick', labelsize = 'x-large')
    mpl.rc('savefig', directory = '/Users/michaelramm/Downloads/', dpi=300)
    mpl.rc('legend', fontsize = 'x-large')

mpl_for_saving()

#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

figure = pyplot.figure()

def plot_for_saving():
    figure.se

def shift_x(x):
    return (x + 31.224) * 1000

for dataset in ['1328_44','1330_06', '1331_42','1336_54']:
    dv.cd(['','Experiments','Spectrum729','2014Jan23',dataset])
    dv.open(1)
    data = dv.get().asarray
    x = data[:,0]
    y = data[:,1]
    excitation_time = dv.get_parameter('Spectrum.manual_excitation_time')
    pyplot.plot(shift_x(x), y,'o-', label = 'Excitation {}'.format(excitation_time))

#pyplot.title('Fast Rabi Flops', fontsize = 40)
#pyplot.xlabel(r'Time $\mu s$', fontsize = 32)
#pyplot.ylabel('Excitation percentage', fontsize = 32)
pyplot.legend()
pyplot.ylim(0,1)
pyplot.xlim(0,100)
pyplot.savefig('5_radial_modes.pdf')
pyplot.show()
