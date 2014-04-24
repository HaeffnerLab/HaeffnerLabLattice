from qutip import qeye, sigmax, sigmay, tensor
from numpy import exp

class ising_calculator_FM(object):
    def __init__(self, number_of_spins, alpha):
        self.H0, self.H1  = self.construct_hamiltonian(number_of_spins, alpha)
    
    def construct_hamiltonian(self, number_of_spins, alpha):
        '''
        following example
        http://qutip.googlecode.com/svn/doc/2.0.0/html/examples/me/ex-24.html
        
        returns H0 - hamiltonian without the B field
        and y_list - list of sigma_y operators
        '''
        N = number_of_spins
        si = qeye(2)
        sx = sigmax()
        sy = sigmay()
        #constructing a list of operators sx_list and sy_list where
        #the operator sx_list[i] applies sigma_x on the ith particle and 
        #identity to the rest
        sx_list = []
        sy_list = []
        for n in range(N):
            op_list = []
            for m in range(N):
                op_list.append(si)
            op_list[n] = sx
            sx_list.append(tensor(op_list))
            op_list[n] = sy
            sy_list.append(tensor(op_list))
        #construct the hamiltonian
        H0 = 0
        #ising coupling term, time independent
        for i in range(N):
            for j in range(N):
                if i < j:
                    H0 -= abs(i - j)**-alpha * sx_list[i] * sx_list[j]
        H1 = 0
        for i in range(N):
            H1 -=  sy_list[i]
        return H0, H1
    
    def get_H(self):
        return self.H0, self.H1