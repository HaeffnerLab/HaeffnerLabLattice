from qutip import mesolve, Qobj, tensor, qsave, qload, Odeoptions
from ising_hamiltonian_time_dependent import ising_calculator_FM
from scripts.theory.time_independent.state_quantifier import state_quantifier
import numpy as np

number_spins = 4
alpha = 1.
Bstart = 50.0 #units of J0
Bstop = 0.01 #units of J0
ramp_time = 0.01 #units of 1/J0
t_list = np.linspace(0, ramp_time , 2)

opts = Odeoptions()
opts.nsteps = 100000
# opts.max_step = 1e-5
# opts.tidy = False
# opts.rtol = 1e-16
print opts

def process_rho(t, state):
    print 'time t'
    print state
    
def exp_ramp(t):
    return Bstop + (Bstart - Bstop) * exp( -t / ramp_time)
    

def run_simulation():
    up_y = Qobj([[1],[1.j]]).unit()
    #initial state, is up y 
    initial_state = tensor([up_y] * number_spins)
    calc = ising_calculator_FM(number_spins, alpha)
    H0,Ht = calc.get_H()
    #time dependent hamiltonian
    #exponential ramping
    H = [H0, [Ht, 'Bstop + (Bstart - Bstop) * exp(-t / tau)']]
    #linear ramping
#     H = [H0, [Ht, 'Bstart + (Bstop - Bstart) * t / ramp_time']]
    args = {'Bstop':Bstop, 'Bstart':Bstart, 'ramp_time':ramp_time}
    print 'Solving'
    data = mesolve(H, initial_state, t_list, [], process_rho, args = args, options = opts)
    print 'Done Solving'
    qsave(data, 'simdata0')

def plot_simulation():
    quant = state_quantifier(number_spins)
    data = qload('simdata0')
    for state in data.states[:]:
        print quant.absolute_magnetization_x(state)

run_simulation() 
# plot_simulation()