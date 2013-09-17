from time_evolution import do_dephasing_dm
from qutip import basis, Qobj, tensor, ket2dm, qeye
import numpy as np


'''test the dephasing'''
#example with diagonal reduced density matrix
# up_y = Qobj([[1],[1.j]]).unit()
# down_y = Qobj([[1],[-1.j]]).unit()
# state  = tensor(up_y, down_y) + tensor(down_y, up_y)
# state = state.unit()
# correlated = ket2dm(state)
# print correlated
# print do_dephasing_dm(correlated, 2)


#example with a non-diagonal density matrix
si = qeye(2)
up_x = Qobj([[1],[1]])
up_z = basis(2,0)
down_z = basis(2,1)

m = ket2dm((tensor(up_z, up_x) + tensor(up_x, up_z)).unit())
print do_dephasing_dm(m, 2)
red = m.ptrace(0)
energies,(state0,state1)= red.eigenstates()

R1 = tensor(state0, si) * tensor(up_z.dag(), si)
R2 = tensor(state1, si) * tensor(down_z.dag(), si)

rot = (R1 + R2).dag() * m * (R1 + R2)
dephased_rot = do_dephasing_dm(rot, 2)
print dephased_rot
dephased_back = (R1 + R2) * dephased_rot * (R1 + R2).dag()
print dephased_back