from qutip import Odeoptions, mesolve
from ising_hamiltonian_time_dependent import ising_calculator_FM
import numpy as np

class time_dependent_simulator(object):
    def __init__(self, number_spins, alpha, opts = Odeoptions()):
        self.opts = opts
        calc = ising_calculator_FM(number_spins, alpha)
        H0,Ht = calc.get_H()
        #time dependent hamiltonian with exponential ramping of Ht
        self.H = [H0, [Ht, 'Bstop + (Bstart - Bstop) * exp(-t / ramp_time)']]
        
    def run_simulation(self, initial_state, Bstart, Bstop, ramp_time, t_list):
        args = {'Bstop':Bstop,
                'Bstart':Bstart,
                'ramp_time':ramp_time
                }
        print 'Solving'
        data = mesolve(self.H, initial_state, t_list, [], [], args = args, options = self.opts)
        print 'Done Solving'
        return data
    
    def ramp_time_exp(self, Bstart, Bstop, ramp_time, t_list):
        return Bstop + (Bstart - Bstop) * np.exp(-t_list / ramp_time)

    def ramp_time_lin(self, Bstart, Bstop, ramp_time, t_list):
        return Bstart + (Bstop - Bstart) * t_list / ramp_time
    
class time_independent_simulator(object):
    def __init__(self, number_spins, alpha, B_field, opts = Odeoptions()):
        self.opts = opts
        calc = ising_calculator_FM(number_spins, alpha)
        H0,Ht = calc.get_H()
        #time dependent hamiltonian with exponential ramping of Ht
# self.H = [H0, [Ht, 'Bstop + (Bstart - Bstop) * exp(-t / ramp_time)']]
        self.H = H0 + Ht * B_field
        
    def run_simulation(self, initial_state, t_list):
        print 'Solving'
        data = mesolve(self.H, initial_state, t_list, [], [], options = self.opts)
        print 'Done Solving'
        return data
    
    def ramp_time_exp(self, Bstart, Bstop, ramp_time, t_list):
        return Bstop + (Bstart - Bstop) * np.exp(-t_list / ramp_time)

    def ramp_time_lin(self, Bstart, Bstop, ramp_time, t_list):
        return Bstart + (Bstop - Bstart) * t_list / ramp_time