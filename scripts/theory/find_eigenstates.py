from ising_calculator import ising_calculator
import numpy as np
from matplotlib import pyplot

number_of_spins = 10
alpha = 1.0
B = 0.5

from qutip import qeye, sigmax, sigmay, tensor, expect
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
    

calc = ising_calculator(number_of_spins, alpha, B)
H = calc.get_H()
# energy,state = H.groundstate()
# print energy, state
# print state[0:10]
# print state.norm()
# print expect(sx_list[3] , state)

energies, states = H.eigenstates(sort = 'low', eigvals = 5)
for i in range(number_of_spins):
    print expect(sy_list[i] , states[3])
