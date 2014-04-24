from ising_calculator import ising_calculator_AFM
import numpy as np
from matplotlib import pyplot

number_of_spins = 10
alpha = 1.0
B_list = np.linspace(0.0, 0.7, 50)

def calculate_and_save():
    energies = np.empty((B_list.size, 2**number_of_spins))
    for i,B in enumerate(B_list):
        print i
        calc = ising_calculator_AFM(number_of_spins, alpha, B)
        energies[i,:] = calc.find_energies()
    np.save('energy_array', energies)


plot_lowest_energies = 10
def load_and_plot():
    energy_array = np.load('energy_array.npy')
#     energy_array = np.load('energy_array_alpha0p5.npy') d
    #subctact lowest energy
    for i in range(plot_lowest_energies):
        plot_energy = energy_array[:,i] - energy_array[:, 0]
        pyplot.plot(B_list, plot_energy) 
    pyplot.ylim([-0.05,1.05])
    pyplot.xlim([-0.05, 0.75])
    pyplot.xlabel('B/J0')
    pyplot.ylabel('(E - E0)/J0')
    pyplot.title('figure 1A, AFM coupling')
    pyplot.show()
    
    
    
# calculate_and_save()
load_and_plot()