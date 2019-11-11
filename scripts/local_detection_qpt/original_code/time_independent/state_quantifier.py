import numpy as np
from qutip import tensor, Qobj, expect, qeye, sigmaz, sigmay, sigmax
import itertools
from scipy.misc import comb as choose

class state_quantifier(object):
    
    def __init__(self, number_of_spins):
        self.N = number_of_spins
        self.possible_spin_states = self.generate_all_possible_combinations(number_of_spins)
        
    def generate_all_possible_combinations(self, number_of_spins):
        '''
        takes the number of spins i. e
        and returns all possible combinations of spins being up and down in the form
        [[1 ,1, 1]
         [1, 1, 0]
         [1, 0, 1]
         [0, 1, 1]
         [1, 0, 0]
         [0, 1, 0]
         [0, 0, 1]
         [0, 0, 0]]
        '''
        N = number_of_spins
        all_combinations = []
        all_states = []
        for number_up in range(N + 1):
            combs = itertools.combinations(np.arange(N), number_up)
            for comb in combs:
                all_combinations.append(list(comb))
        for which_up in all_combinations:
            state_list = np.ones(N)
            state_list[which_up] = 0
            all_states.append(state_list)
        return all_states
    
    def state_to_tensor(self, state):
        '''
        takes the state i.e [0, 1, 0, 0]
        and converts it to a composite qubit state of all the spins
        ith entry 0 corresponds to ith spin being up, and 1 to down
        '''
        def selector(num):
            up_x = Qobj([1,1]).unit().dag()
            down_x = Qobj([1,-1]).unit().dag()
            if num == 0:
                return up_x
            else:
                return down_x
        return tensor([selector(i) for i in state])
        
    def absolute_magnetization_x(self, input_state):
        '''
        calculates the absolute magnization in the x direction by taking the overlap with every possible
        combination of N spins
        '''
        probs = np.zeros(self.N + 1)
        for state in self.possible_spin_states:
            total_up = self.N - state.sum()
            qstate = self.state_to_tensor(state)
            overlap = qstate.dag() * input_state
            probability = np.abs(overlap.diag())**2
            probs[int(total_up)] += probability
        ns = np.arange(self.N + 1)
        m_x = probs * np.abs(self.N - 2 * ns) / float(self.N)
        m_x = m_x.sum()
        scaling = choose(self.N, ns) * np.abs(self.N - 2*ns) / float(self.N * 2 ** self.N)
        scaling = scaling.sum()
        m_x_bar = (scaling - m_x) / (scaling - 1)
        return m_x_bar
    
    def get_reduced_dms(self,states, spin):
        '''
        takes a number of states and returns a list of bloch vector of the 0th spin coordinates for each
        '''
        sz = sigmaz()
        sy = sigmay()
        sx = sigmax()
        zs = []
        ys = []
        xs = []
        for state in states:
            ptrace = state.ptrace(spin)
            zval = abs(expect(sz, ptrace ))
            yval = abs(expect(sy, ptrace ))
            xval = abs(expect(sx, ptrace ))
            zs.append(zval)
            ys.append(yval)
            xs.append(xval)
        return xs,ys,zs