import fractions

class EnergyLevel():
    
    spectoscopic_notation = {
                            'S': 0,
                            'P': 1, 
                            'D': 2,
                            }
    
    def __init__(self, angular_momentum_l, total_angular_momentum_j, spin_s = 1./2.):
        if type(angular_momentum_l) == str:
            angular_momentum_l = self.spectoscopic_notation[angular_momentum_l]
        S = spin_s
        L = angular_momentum_l
        J = total_angular_momentum_j
        self.g = self.lande_factor(S, L, J)
    
    def lande_factor(self, S, L ,J):
        g = 3./2. + ( S * (S + 1.) - L * (L + 1.)) / ( 2.*J*(J + 1.))
        return g
    
EnergyLevel('S', 1./2.)
EnergyLevel('D', 5./2.)
