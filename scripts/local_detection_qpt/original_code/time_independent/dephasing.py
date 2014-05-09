from ising_calculator import ising_calculator_FM
from scripts.theory.time_dependent.time_evolution import do_dephasing_dm, get_dms
import numpy as np
from matplotlib import pyplot
from qutip import ket2dm, tensor, qeye
from qutip.metrics import tracedist
# from scripts.theory.time_dependent.integrator import time_independent_simulator


def apply_dephasing(number_of_spins, alpha, B):
    '''
    takes number of spins, alpha, and the magnetic field and returns the
    FM hamiltonian along with its ground state and the dephased ground state
    '''
    calc = ising_calculator_FM(number_of_spins, alpha, B)
    H = calc.get_H()
    energy,groundstate = H.groundstate()
    dm_groundstate = ket2dm(groundstate)
    dephased = do_dephasing_dm(dm_groundstate, number_of_spins)
    return H, dm_groundstate, dephased

def get_max_trace_distnace(t_list, H, dm_groundstate, dephased):
    '''
    given a list of times, the unitary evolution hamiltonian and two density matrices, computes
    the maximum subsequent trace distance between the two states.
    '''
    rhos_ground = []
    rhos_dephased = []
    trace_distances = []
    for t in t_list:
        time_evol = -H * 1.j * t
        rho_ground =  time_evol.expm() * dm_groundstate * (time_evol.expm().dag())
        rhos_ground.append(rho_ground)
        rho_dephased =  time_evol.expm() * dephased * (time_evol.expm().dag())
        rhos_dephased.append(rho_dephased)
        trace_distances.append(tracedist(rho_ground.ptrace(0), rho_dephased.ptrace(0)))
    max_trace_distace = np.array(trace_distances).max()
    return rhos_ground, rhos_dephased, trace_distances, max_trace_distace

def plot_time_evolution(rhos_ground, rhos_dephased, trace_distances, t_list):
    pyplot.figure('evolution')
    xs,ys,zs = get_dms(rhos_ground)
    pyplot.plot(t_list, ys, label = 'ground')
    xs_dephased,ys_dephased,zs_dephased = get_dms(rhos_dephased)
    pyplot.plot(t_list, ys_dephased, label = 'dephased y')
    pyplot.plot(t_list, trace_distances, label = 'trace distance')
    pyplot.ylabel('Density matrix y component')
    pyplot.ylim([-1.05,1.05])
    pyplot.legend()
    pyplot.show()
    
def dephase_and_plot_evolution(number_of_spins, alpha, B, t_list):
    H, dm_groundstate, dephased = apply_dephasing(number_of_spins, alpha, B)
    rhos_ground, rhos_dephased, trace_distances, max_trace_distace = get_max_trace_distnace(t_list, H, dm_groundstate, dephased)
    plot_time_evolution(rhos_ground, rhos_dephased, trace_distances, t_list)
    print 'max trace distance', max_trace_distace


if __name__ == '__main__':
    def simple_plot():
        number_of_spins = 10
        alpha = 1.0
        B = 1.0
        t_list = np.linspace(0, 20 , 500)
        dephase_and_plot_evolution(number_of_spins, alpha, B, t_list)
        
    def max_distance_for_B():
        '''
        computes the maximum trace distance for various values of B
        '''
        pts = 30
        number_of_spins = 2
        alpha = 1.0
        B_list = np.logspace(-1, 1, pts)
        t_list = np.linspace(0, 20 , 500)
        max_distances = []
        for B in B_list:
            print B
            H, dm_groundstate, dephased = apply_dephasing(number_of_spins, alpha, B)
            rhos_ground, rhos_dephased, trace_distances, max_trace_distace = get_max_trace_distnace(t_list, H, dm_groundstate, dephased)
            max_distances.append(max_trace_distace)
        np.save('trace distances {} pts'.format(pts), (B_list,max_distances))
    
    max_distance_for_B()
#     simple_plot()


#     integ = time_independent_simulator(number_of_spins, alpha, B)
# data = integ.run_simulation(dephased, t_list)
# xs_integ_dephased,ys_integ_dephased,zs_integ_dephased = get_dms(data.states)
# pyplot.plot(t_list, ys_integ_dephased, label = 'dephased, integrator')

# def nice_print_dm(dm):
#     print np.abs(dm.full())
# nice_print_dm(dm_groundstate)
# nice_print_dm(dephased)
# nice_print_dm(ket2dm(dephased_other))
# energies,all_states = H.eigenstates()
# occupations = []
# for state in all_states:
#     occupations.append( np.abs((state.dag() * dephased * state).diag()[0]) )
# occupations = np.array(occupations)
# shifted_energy = energies - energies.min()

# print occupations
# print shifted_energy


# pyplot.figure('energy spectrum')
# pyplot.plot(shifted_energy, occupations, 'g*', label = 'exact')

# signal_size = len(ys_dephased)
# timestep = t_list[1] - t_list[0]
# fft = np.abs(np.fft.fft(ys_dephased))
#normalize area to 1
# fft = fft / np.sum(fft)
# fft_freq = np.fft.fftfreq(signal_size, timestep)
# pyplot.plot(fft_freq * 2 * np.pi, fft, 'r', label = 'fft')
