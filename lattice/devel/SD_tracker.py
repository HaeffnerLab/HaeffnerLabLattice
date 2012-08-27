from fractions import Fraction as Frac
import math
from labrad import types as T, units as U
    
class EnergyLevel():
    
    bohr_magneton = T.Value(9.274e-24,'J/T')
    
    spectoscopic_notation = {
                            'S': 0,
                            'P': 1, 
                            'D': 2,
                            }
    
    def __init__(self, angular_momentum_l, total_angular_momentum_j, spin_s = '1/2'):
        if type(angular_momentum_l) == str:
            angular_momentum_l = self.spectoscopic_notation[angular_momentum_l]
        total_angular_momentum_j = Frac(total_angular_momentum_j)
        spin_s = Frac(spin_s)
        S = spin_s
        L = angular_momentum_l
        J = J = total_angular_momentum_j
        self.g = self.lande_factor(S, L, J)
        #sublevels are found, 2* self.J is always an integer, so can use numerator
        self.sublevels_m =  [-J + i for i in xrange( 1 + (2 * J).numerator)]
    
    def lande_factor(self, S, L ,J):
        '''computes the lande g factor'''
        g = Frac(3,2) + Frac( S * (S + 1) - L * (L + 1) ,  2 * J*(J + 1))
        return g
    
    def energies(self, B):
        energy_scale = (self.bohr_magneton * B.inUnitsOf('T') / U.hplanck).inUnitsOf('MHz')
        energies = [energy_scale * m for m in self.sublevels_m]
        return zip(self.sublevels_m,energies)
    
S = EnergyLevel('S', '1/2').energies(T.Value(100, 'uT'))
D = EnergyLevel('D', '5/2').energies(T.Value(100, 'uT'))

allowed_transitions = [0,1,2]
carriers = []
for m_s,E_s in S:
    for m_d,E_d in D:
        if abs(m_d-m_s) in allowed_transitions:
            print str(m_d)
            carriers.append('S' + str(m_s) + 'D' + str(m_d))
print carriers        