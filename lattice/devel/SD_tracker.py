from fractions import Fraction
from labrad import types as T, units as U
    
class EnergyLevel():
    
    bohr_magneton = T.Value(9.274e-24,'J/T')
    
    spectoscopic_notation = {
                            'S': 0,
                            'P': 1, 
                            'D': 2,
                            }
    
    spectoscopic_notation_rev = {
                            0 : 'S',
                            1 : 'P',
                            2 : 'D',
                            }
    
    
    def __init__(self, angular_momentum_l, total_angular_momentum_j, spin_s = '1/2'):
        #convert spectroscopic notation to the spin number
        if type(angular_momentum_l) == str:
            angular_momentum_l = self.spectoscopic_notation[angular_momentum_l]
        total_angular_momentum_j = Fraction(total_angular_momentum_j)
        spin_s = Fraction(spin_s)
        S = spin_s
        self.L = L = angular_momentum_l
        J = total_angular_momentum_j
        lande_factor =  self.lande_factor(S, L, J)
        #sublevels are found, 2* self.J is always an integer, so can use numerator
        self.sublevels_m =  [-J + i for i in xrange( 1 + (2 * J).numerator)]
        self.energy_scale = (lande_factor * self.bohr_magneton / U.hplanck) #1.4 MHz / gauss
    
    def lande_factor(self, S, L ,J):
        '''computes the lande g factor'''
        g = Fraction(3,2) + Fraction( S * (S + 1) - L * (L + 1) ,  2 * J*(J + 1))
        return g
    
    def magnetic_to_energy(self, B):
        #given the magnitude of the magnetic field, returns all energies of all zeeman sublevels
        energies = [(self.energy_scale * m * B.inUnitsOf('T')).inUnitsOf('MHz') for m in self.sublevels_m]
        representations = [self.frac_to_string(m) for m in self.sublevels_m]
        return zip(self.sublevels_m,energies,representations)
    
    def frac_to_string(self, sublevel):
        #helper class for converting energy levels to strings
        sublevel = str(sublevel)
        if not sublevel.startswith('-'): 
            sublevel = '+' + sublevel
        together = self.spectoscopic_notation_rev[self.L] + sublevel
        return together
    
class Transitions_SD():
    
    S = EnergyLevel('S', '1/2')
    D = EnergyLevel('D', '5/2')
    allowed_transitions = [0,1,2]
    B = None
    
    def set_magnetic_field(self, B):
        self.B = B.inUnitsOf('T')
    
    def get_transition_energies(self):
        if self.B is None: raise Exception ("Magnetic Field Not Specified")
        ans = []
        for m_s,E_s,repr_s in self.S.magnetic_to_energy(self.B):
            for m_d,E_d,repr_d in self.D.magnetic_to_energy(self.B):
                if abs(m_d-m_s) in self.allowed_transitions:
                    name = repr_s + repr_d
                    diff = E_d - E_s
                    ans.append((name, diff))
        return ans
    
    def energies_to_magnetic_field(self, energies):
        #given two points in the form ((-1/2,5+/2, 1.0 MHz), (-1/2, 5+/2, 2.0 MHz)), calculates the magnetic field and the zero-field transition frequency
        s_energy_scale = self.S.energy_scale
        d_energy_scale = self.D.energy_scale
        
        

transitions = Transitions_SD()
transitions.set_magnetic_field(T.Value(100, 'uT'))
ans = transitions.get_transition_energies()
print ans