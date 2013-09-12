from ising_calculator import ising_calculator_FM
from state_quantifier import state_quantifier
import numpy as np
from matplotlib import pyplot

number_of_spins = 6
alpha = 1.0
B_list = np.logspace(-2, 2, 100)

def calculate_and_save():
    magnetization_array = np.empty_like(B_list)
    quant = state_quantifier(number_of_spins)
    for i,B in enumerate(B_list):
        print i
        calc = ising_calculator_FM(number_of_spins, alpha, B)
        H = calc.get_H()
        energy,groundstate = H.groundstate()
        m = quant.absolute_magnetization_x(groundstate)
        magnetization_array[i] = m
    np.save('magnetization_array_{}'.format(number_of_spins), magnetization_array)

def load_and_plot():
    pyplot.xscale('log')
    pyplot.plot(B_list, np.load('magnetization_array_6.npy'), label = '6 spins')
    pyplot.plot(B_list, np.load('magnetization_array_4.npy'), label = '4 spins')
    pyplot.plot(B_list, np.load('magnetization_array_2.npy'), label = '2 spins')
    pyplot.ylim([-0.05,1.05])
    pyplot.xlim([0.05, 50.05])
    pyplot.xlabel('B/J0')
    pyplot.ylabel('Magnetization')
    pyplot.title('figure 3a, Magnetization')
    pyplot.legend()
    pyplot.show()
    
    
# calculate_and_save()
load_and_plot()