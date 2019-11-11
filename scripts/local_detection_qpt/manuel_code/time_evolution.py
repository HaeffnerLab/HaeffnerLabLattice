from qutip import mesolve, Qobj, tensor, qsave, qload, Odeoptions, qeye, sigmax, sigmay, sigmaz, expect, ket2dm, basis, matrix_histogram_complex
from integrator import time_dependent_simulator
import numpy as np
from matplotlib import pyplot

number_spins = 5
alpha = 1.
Bstart = 50.0 #units of J0
Bstop = 0.01 #units of J0
ramp_time = 5. #units of 1/J0
t_list = np.linspace(0, 12 * ramp_time , 2000)

#set up integrator options
opts = Odeoptions()
opts.nsteps = 10000000

def all_spins_up_y():
    up_y = Qobj([[1],[1.j]]).unit()
    state = tensor([up_y] * number_spins)
    return state

def plot_magnetization(states, b_fields):
    from scripts.theory.time_independent.state_quantifier import state_quantifier
    quant = state_quantifier(number_spins)
    ms = [quant.absolute_magnetization_x(state) for state in states]
    pyplot.xscale('log')
    pyplot.plot(b_fields, ms)
    pyplot.ylim([-0.05,1.05])
    pyplot.xlim([0.05, 50.05])
    pyplot.xlabel('B/J0')
    pyplot.ylabel('Magnetization')
    pyplot.title('Magnetization ramped')
    pyplot.show()
    
def get_dms(states):
    '''
takes a number of states and returns a list of bloch vector coordinates for each
'''
    si = qeye(2)
    sz = sigmaz()
    sy = sigmay()
    sx = sigmax()
    zs = []
    ys = []
    xs = []
    for state in states:
        ptrace = state.ptrace(0)
        zval = expect(sz, ptrace )
        yval = expect(sy, ptrace )
        xval = expect(sx, ptrace )
        zs.append(zval)
        ys.append(yval)
        xs.append(xval)
    return xs,ys,zs
        

def plot_density_matrix(states, b_fields):
    xs,ys,zs = get_dms(states)
    pyplot.xscale('log')
    pyplot.ylabel('Populations of ion 0')
    pyplot.title('Density matrix')
    pyplot.plot(b_fields, zs, 'x', label = 'z')
    pyplot.plot(b_fields, ys, label = 'y')
    pyplot.plot(b_fields, xs, '*', label = 'x')
    pyplot.ylim([-0.05,1.05])
    pyplot.xlim([0.05, 50.05])
    pyplot.xlabel('B/J0')
    pyplot.legend()
    pyplot.show()

def make_dephased_plot(b_list_before_dephase, data_before, b_list_after_dephase, data_after_undephased, data_after_dephased):
    pyplot.figure()
    xs,ys,zs = get_dms(data_before.states)
    pyplot.plot(b_list_before_dephase, ys, 'black', label = 'preparation')
    xs,ys,zs = get_dms(data_after_undephased.states)
    pyplot.plot(b_list_after_dephase, ys, 'r', label = 'undephased')
    xs,ys,zs = get_dms(data_after_dephased.states)
    pyplot.plot(b_list_after_dephase, ys, 'b', label = 'dephased')
    pyplot.xscale('log')
    pyplot.ylim([-0.25,1.05])
    pyplot.xlim([-0.05, 50.05])
    pyplot.ylabel('Density matrix y component', size = 16)
#     pyplot.title('Ramped B field')
    pyplot.xlabel('B/J0', size = 16)
    pyplot.legend(loc = 'lower left', prop={'size':16})
    pyplot.gca().invert_xaxis()

def make_dephased_plot_time(t_list_before_dephase, data_before, t_list_after_dephase, data_after_undephased, data_after_dephased):
    pyplot.figure('time')
    xs,ys,zs = get_dms(data_before.states)
    pyplot.plot(t_list_before_dephase, ys, 'black', label = 'preparation')
    xs,ys,zs = get_dms(data_after_undephased.states)
    pyplot.plot(t_list_after_dephase, ys, 'r', label = 'undephased')
    xs,ys,zs = get_dms(data_after_dephased.states)
    pyplot.plot(t_list_after_dephase, ys, 'b', label = 'dephased')
    pyplot.ylim([-0.25,1.05])
# pyplot.xlim([0.05, 50.05])
    pyplot.ylabel('Density matrix y component', size = 16)
#     pyplot.title('Ramped B field')
    pyplot.xlabel('Time 1/J0', size=16)
    pyplot.legend(loc = 'lower left', prop={'size':16})

def do_dephasing_dm(dm, number_spins):
    '''
takes the state and returns the dephased densitry matrix after projecting the 0th ion onto its eigenbasis
'''
    N = number_spins
    si = qeye(2)
    ptrace = dm.ptrace(0)
#     matrix_histogram_complex(ptrace)
    print ptrace
    overlap,eigenstate = ptrace.eigenstates()
    projection0 = [si] * N
    projection0[0] = ket2dm(eigenstate[0])
    projection0 = tensor(projection0)
    projection1 = [si] * N
    projection1[0] = ket2dm(eigenstate[1])
    projection1 = tensor(projection1)
    #proj is the projection onto th eigenbasis of particle 0
    dephased = projection0 * dm * projection0 + projection1 * dm * projection1
    #dephasing checks
# environment = range(1,N)
# print 'do partial traces agree?', [dm.ptrace(i) == dephased.ptrace(i) for i in range(N)], dm.ptrace(environment) == dephased.ptrace(environment)
# print 'but the dm is different?', not dephased == dm
    return dephased

def do_dephasing(state, number_spins):
    return do_dephasing_dm(ket2dm(state), number_spins)

if __name__ == '__main__':
    integrator = time_dependent_simulator(number_spins, alpha, opts)
    '''
run the simulator starting with all spins up
'''
    # initial_state = all_spins_up_y()
    # data = integrator.run_simulation(initial_state, Bstart, Bstop, ramp_time, t_list)
    # qsave(data, 'simdata0')
    '''
make magnetization plot
'''
    # data = qload('simdata0')
    # b_list = integrator.ramp_time_exp(Bstart, Bstop, ramp_time, t_list)
    # plot_magnetization(data.states, b_list)
    '''
make density matrix plot
'''
    # data = qload('simdata0')
    # b_list = integrator.ramp_time_exp(Bstart, Bstop, ramp_time, t_list)
    # plot_density_matrix(data.states, b_list)
    '''
run the simulator with dephasing
'''
    dephasing_B = 5
    b_list = integrator.ramp_time_exp(Bstart, Bstop, ramp_time, t_list)
    dephasing_time = t_list[np.argmin(np.abs(b_list - dephasing_B))]
    t_list_prior_dephase = t_list[t_list <= dephasing_time]
    t_list_after_dephase = t_list[t_list >= dephasing_time]
    initial_state = all_spins_up_y()
    data_before = integrator.run_simulation(initial_state, Bstart, Bstop, ramp_time, t_list_prior_dephase)
    correlated_state = data_before.states[-1]
    dephased_state = do_dephasing(correlated_state, number_spins)
    #continue the time evolution for both dephasing and undephasing state
    data_after_undephased = integrator.run_simulation(correlated_state, dephasing_B, dephasing_B, ramp_time, t_list_after_dephase)
    data_after_dephased = integrator.run_simulation(dephased_state, dephasing_B, dephasing_B, ramp_time, t_list_after_dephase)
#     data_after_undephased = integrator.run_simulation(correlated_state, Bstart, Bstop, ramp_time, t_list_after_dephase)
#     data_after_dephased = integrator.run_simulation(dephased_state, Bstart, Bstop, ramp_time, t_list_after_dephase)
    #plot everything
    b_list_before_dephase = integrator.ramp_time_exp(Bstart, Bstop, ramp_time, t_list_prior_dephase)
    b_list_after_dephase = integrator.ramp_time_exp(Bstart, Bstop, ramp_time, t_list_after_dephase)
#     make_dephased_plot(b_list_before_dephase, data_before, b_list_after_dephase, data_after_undephased, data_after_dephased)
    make_dephased_plot_time(t_list_prior_dephase, data_before, t_list_after_dephase, data_after_undephased, data_after_dephased)
    pyplot.tick_params(axis='both', which='major', labelsize=16)
    pyplot.savefig('dephasing_{}.pdf'.format(dephasing_B), dpi = 300)
    pyplot.show()