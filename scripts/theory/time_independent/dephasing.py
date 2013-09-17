from ising_calculator import ising_calculator_FM
from scripts.theory.time_dependent.time_evolution import do_dephasing_dm, get_dms
import numpy as np
from matplotlib import pyplot
from qutip import ket2dm, tensor, qeye
from scripts.theory.time_dependent.integrator import time_independent_simulator

number_of_spins = 2
alpha = 1.0
B = 0.5
t_list = np.linspace(0, 20 , 500)

si = qeye(2)

def nice_print_dm(dm):
    print np.abs(dm.full())

calc = ising_calculator_FM(number_of_spins, alpha, B)
integ = time_independent_simulator(number_of_spins, alpha, B)
H = calc.get_H()
energy,groundstate = H.groundstate()
energies,all_states = H.eigenstates()

print energies

dm_groundstate = ket2dm(groundstate)
# nice_print_dm(dm_groundstate)
dephased = do_dephasing_dm(dm_groundstate, number_of_spins)

rhos_ground = []
rhos_dephased = []
for t in t_list:
    print t
    time_evol = -H * 1.j * t
    rho =  time_evol.expm() * dm_groundstate * (time_evol.expm().dag())
    rhos_ground.append(rho)
    rho =  time_evol.expm() * dephased * (time_evol.expm().dag())
    rhos_dephased.append(rho)
    
pyplot.figure('evolution')
xs,ys,zs = get_dms(rhos_ground)
pyplot.plot(t_list, ys, label = 'ground')
xs_dephased,ys_dephased,zs_dephased = get_dms(rhos_dephased)
pyplot.plot(t_list, ys_dephased, label = 'dephased')


data = integ.run_simulation(dephased, t_list)
xs_integ_dephased,ys_integ_dephased,zs_integ_dephased = get_dms(data.states)
# pyplot.plot(t_list, ys_integ_dephased, label = 'dephased, integrator')


pyplot.ylabel('Density matrix y component')
pyplot.ylim([-0.05,1.05])
pyplot.legend()

# nice_print_dm(dephased)
# nice_print_dm(ket2dm(dephased_other))

occupations = []
for state in all_states:
    occupations.append( np.abs((state.dag() * dephased * state).diag()[0]) )
occupations = np.array(occupations)
shifted_energy = energies - energies.min()

print occupations
print shifted_energy




pyplot.figure('energy spectrum')
pyplot.plot(shifted_energy, occupations, 'g*', label = 'exact')

signal_size = len(ys_dephased)
timestep = t_list[1] - t_list[0]
fft = np.abs(np.fft.fft(ys_dephased))
#normalize area to 1
fft = fft / np.sum(fft)
fft_freq = np.fft.fftfreq(signal_size, timestep)
pyplot.plot(fft_freq * 2 * np.pi, fft, 'r', label = 'fft')

pyplot.show()