from qutip import qeye, sigmax, sigmay, tensor

class ising_calculator_AFM(object):
    def __init__(self, number_of_spins, alpha, B):
        self.H =self.construct_hamiltonian(number_of_spins, alpha, B)
    
    def construct_hamiltonian(self, number_of_spins, alpha, B):
        '''
following example
http://qutip.googlecode.com/svn/doc/2.0.0/html/examples/me/ex-24.html
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
        H = 0
        #magnetic field term, hamiltonian is in units of J0
        for i in range(N):
            H-= B * sy_list[i]
        #ising coupling term
        for i in range(N):
            for j in range(N):
                if i < j:
                    H+= abs(i - j)**-alpha * sx_list[i] * sx_list[j]
        return H
    
    def find_energies(self):
        return self.H.eigenenergies()
    
    def get_H(self):
        return self.H

class ising_calculator_FM(object):
    def __init__(self, number_of_spins, alpha, B):
        self.H =self.construct_hamiltonian(number_of_spins, alpha, B)
    
    def construct_hamiltonian(self, number_of_spins, alpha, B):
        '''
following example
http://qutip.googlecode.com/svn/doc/2.0.0/html/examples/me/ex-24.html
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
        H = 0
        #magnetic field term, hamiltonian is in units of J0
        for i in range(N):
            H-= B * sy_list[i]
        #ising coupling term
        for i in range(N):
            for j in range(N):
                if i < j:
                    H-= abs(i - j)**-alpha * sx_list[i] * sx_list[j]
        return H
    
    def find_energies(self):
        return self.H.eigenenergies()
    
    def get_H(self):
        return self.H

if __name__ == '__main__':
    number_spins = 10
    alpha = 1
    B = 0.5 #measured in units of J0
    calc = ising_calculator_AFM(number_spins, alpha, B)
    energies = calc.find_energies()
    print energies