from ising_calculator import ising_calculator_FM
from state_quantifier import state_quantifier
import numpy as np
from matplotlib import pyplot

number_of_spins = 5
alpha = 1.0
B_list = np.logspace(3, -3, 100)

def calculate_and_save():
    quant = state_quantifier(number_of_spins)
    ground_states = []
    for i,B in enumerate(B_list):
        print i
        calc = ising_calculator_FM(number_of_spins, alpha, B)
        H = calc.get_H()
        energy,groundstate = H.groundstate()
        ground_states.append(groundstate)
    sx,sy,sz = quant.get_reduced_dms(ground_states, spin = 0)
    np.save('magnetization_array_one_spin_{}'.format(number_of_spins), (B_list,sx,sy,sz))

def load_and_plot():
    pyplot.xscale('log')
    B_list,sx,sy,sz = np.load('magnetization_array_one_spin_5.npy')
    pyplot.plot(B_list, sy , label = '5 spins y')
    pyplot.ylim([-.05,1.05])
    pyplot.xlabel('Magnetic field (B/J0)', fontsize = 16)
    pyplot.ylabel(u'<$\sigma_y^{(0)}$>', fontsize = 16)
    pyplot.title('Local Detection Quantum Ising Model', fontsize = 20)
    pyplot.gca().invert_xaxis()
    pyplot.show()
    
def load_and_plot_together():
    pyplot.xscale('log')
    B_list,sx,sy,sz = np.load('magnetization_array_one_spin_5.npy')
    pyplot.plot(B_list, sy , 'b', label = '5 spins y')
    pyplot.ylim([-.05,1.05])
    pyplot.xlabel('Magnetic field (B/J0)', fontsize = 16)
    pyplot.ylabel(u'<$\sigma_y^{(0)}$>', fontsize = 16, color ='b')
    pyplot.title('Local Detection Quantum Ising Model', fontsize = 20)
    for tl in pyplot.gca().get_yticklabels():
        tl.set_color('b')
    pyplot.gca().invert_xaxis()
    #also plot max local distance on the same set of axis
    B_list, dist = np.load('trace distances 30 pts.npy')
    ax2 = pyplot.twinx()
    
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    ax2.set_ylabel('Trace Distance', color='r', fontsize = 16)
    ax2.plot(B_list, dist, 'r')
    pyplot.xlim(10**3, 10**-3)
    pyplot.ylim(-.05/2., 1.05/2.)
    pyplot.show()
    
def load_and_find(magnetization):
    '''
    finds the b fields for a given magnetization
    '''
    B_list,sx,sy,sz = np.load('magnetization_array_one_spin_5.npy')
    index = np.argmin(np.abs(magnetization - sy))
    return B_list[index]
    
# calculate_and_save()
# load_and_plot()
load_and_plot_together()
#print [load_and_find(B) for B in [0.85, 0.5, 0.15]] #[1.873817422860383, 0.93260334688321989, 0.30538555088334157]