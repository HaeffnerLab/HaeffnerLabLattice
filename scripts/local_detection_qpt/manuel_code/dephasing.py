from ising_calculator import ising_calculator_AFM,ising_calculator_FM
from time_evolution import do_dephasing_dm, get_dms
import numpy as np
from matplotlib import pyplot
from qutip import ket2dm, tensor, mesolve,basis,Qobj
from qutip.metrics import tracedist
from time import time
import mpmath as mp
# from scripts.theory.time_dependent.integrator import time_independent_simulator


def apply_dephasing(number_of_spins, alpha, B,fm_str = 'AFM',kT = 0.0):
    '''
    takes number of spins, alpha, and the magnetic field and returns the
    hamiltonian along with its ground state and the dephased ground state
    choose fm_str = 'FM' for ferromagnetic interaction, and 'AFM' for anti-ferromagnetic 
    '''
    if fm_str == 'FM':
        calc = ising_calculator_FM(number_of_spins, alpha, B)
    elif fm_str == 'AFM':
        calc = ising_calculator_AFM(number_of_spins, alpha, B)
    H = calc.get_H()
    if kT == 0.0:
        energy,groundstate = H.groundstate()
        dm_groundstate = ket2dm(groundstate)
    else:
        Hdata = H.data.todense()
        arr_mp = mp.matrix(-Hdata /kT)
        exp_mp = mp.expm(arr_mp)
        trace = np.array(exp_mp.tolist()).trace()
        normalized_mp = exp_mp / trace
        normalized_np = np.array(normalized_mp.tolist(), dtype = np.complex)
        dm_groundstate = Qobj(normalized_np, dims = 2 * [number_of_spins*[2]])
    dephased = do_dephasing_dm(dm_groundstate, number_of_spins)
    return H, dm_groundstate, dephased

def get_max_trace_distance(t_list, H, dm_groundstate, dephased):
    '''
    given a list of times, the unitary evolution hamiltonian and two density matrices, computes
    the maximum subsequent trace distance between the two states.
    '''
    rhos_dephased = mesolve(H,dephased,t_list,[],[]).states
    trace_distances = []
    for rho_dephased in rhos_dephased:
        trace_distances.append(tracedist(dm_groundstate.ptrace(0), rho_dephased.ptrace(0)))
    max_trace_distace = np.array(trace_distances).max()
    total_trace_distance = get_total_distance(dm_groundstate,dephased)
    return dm_groundstate, rhos_dephased, trace_distances, max_trace_distace, total_trace_distance

def get_total_distance(dm_groundstate,dephased):
    return tracedist(dm_groundstate,dephased)

def plot_time_evolution(rhos_ground, rhos_dephased, trace_distances, total_trace_distance, t_list):
    pyplot.figure('evolution')
    xs,ys,zs = get_dms(rhos_ground)
    pyplot.plot(t_list, ys, label = 'ground')
    xs_dephased,ys_dephased,zs_dephased = get_dms(rhos_dephased)
    pyplot.plot(t_list, ys_dephased, label = 'dephased y')
    pyplot.plot(t_list, trace_distances, label = 'trace distance')
    pyplot.plot(t_list, [total_trace_distance]*len(t_list), label = 'total trace distance')
    pyplot.ylabel('Density matrix y component')
    pyplot.ylim([-1.05,1.05])
    pyplot.legend()
    pyplot.show()
    
def dephase_and_plot_evolution(number_of_spins, alpha, B, t_list):
    H, dm_groundstate, dephased = apply_dephasing(number_of_spins, alpha, B)
    rhos_ground, rhos_dephased, trace_distances, max_trace_distace, total_trace_distance = get_max_trace_distance(t_list, H, dm_groundstate, dephased)
    print 'max trace distance', max_trace_distace
    plot_time_evolution([rhos_ground]*number_of_spins, rhos_dephased, trace_distances, total_trace_distance, t_list)


if __name__ == '__main__':
    def simple_plot():
        number_of_spins = 4
        alpha = 1.0
        B = 0.02
        t_list = np.linspace(0, 3000 , 2000)
        dephase_and_plot_evolution(number_of_spins, alpha, B, t_list)
        
    def max_distance_for_B(spins,alpha,fm_str,kT = 0):
        '''
        computes the maximum trace distance for various values of B
        '''
        pts = 200
        t_max = 10
        number_of_spins = spins
        t_res = 2000
        t_res = 200
        B_list = np.logspace(-2, 1, pts)
        t_list = np.linspace(0, 200 , t_res)
        t_list = np.linspace(0,t_max,t_res)
        max_distances = []
        total_distances = []
        for B in B_list:
            t1 = time()
            print spins,B
            H, dm_groundstate, dephased = apply_dephasing(number_of_spins, alpha, B,fm_str,kT)
#             matrix_histogram_complex(dm_groundstate)
#             pyplot.show()
#             print 'population in the all-up state:', (tensor([basis(2,0)]*number_of_spins).dag()*dm_groundstate*tensor([basis(2,0)]*number_of_spins)).data
#             print 'population in the all-down state:', (tensor([basis(2,1)]*number_of_spins).dag()*dm_groundstate*tensor([basis(2,1)]*number_of_spins)).data
#             print tensor(basis(2,0),basis(2,1)).dag()*dm_groundstate*tensor(basis(2,0),basis(2,1))
#             print tensor(basis(2,1),basis(2,0)).dag()*dm_groundstate*tensor(basis(2,1),basis(2,0))
            rhos_ground, rhos_dephased, trace_distances, max_trace_distace, total_trace_distance = get_max_trace_distance(t_list, H, dm_groundstate, dephased)
            max_distances.append(max_trace_distace)
            total_distances.append(total_trace_distance)
            t2 = time()
            print '{:.2f} seconds'.format(t2-t1)
        np.save(fm_str+'/trd_spins_{}_pts_{}_t_res_{}_t_max_{}_alpha_{}_kT_{}'.format(number_of_spins,pts,t_res,t_max,alpha,kT), (B_list,max_distances,total_distances))
#         np.save(fm_str+'/trd_spins_{}_pts_{}_t_res_{}_alpha_{}'.format(number_of_spins,pts,t_res,alpha), (B_list,max_distances,total_distances))
#         pyplot.plot(B_list,max_distances, label = 'maximum trace distance')
#         pyplot.plot(B_list,total_distances, label = 'total trace distance')
#         pyplot.xscale('log')
#         pyplot.legend()
#         pyplot.show()
    
    alpha = 1.0
    spins = number_of_spins = 3
    kT = 0
    B = 1
    fm_str 'FM'
    H, dm_groundstate, dephased = apply_dephasing(number_of_spins, alpha, B,fm_str,kT)
#     for fm_str in ['FM','AFM']:  #Can be either 'AFM' or 'FM' for (Anti)Ferromagnet 
#     kT_list = np.linspace(0,10,11)
#     print kT_list
#     for kT in kT_list:
#         for spins in range(2,7):
#         max_distance_for_B(spins,alpha,fm_str,kT=kT)
            
#     fm_str = 'AFM'  #Can be either 'AFM' or 'FM' for (Anti)Ferromagnet 
#     alpha = 1.0
#     spins = 6
#     kT_list = np.linspace(0,1.0,10)
#     for kT in kT_list:
#         for spins in range(2,7):
#             max_distance_for_B(spins,alpha,fm_str,kT=kT)

#     simple_plot()


# integ = time_independent_simulator(number_of_spins, alpha, B)
# data = integ.run_simulation(dephased, t_list)
# xs_integ_dephased,ys_integ_dephased,zs_integ_dephased = get_dms(data.states)
# pyplot.plot(t_list, ys_integ_dephased, label = 'dephased, integrator')

# def nice_print_dm(dm):
# print np.abs(dm.full())
# nice_print_dm(dm_groundstate)
# nice_print_dm(dephased)
# nice_print_dm(ket2dm(dephased_other))
# energies,all_states = H.eigenstates()
# occupations = []
# for state in all_states:
# occupations.append( np.abs((state.dag() * dephased * state).diag()[0]) )
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