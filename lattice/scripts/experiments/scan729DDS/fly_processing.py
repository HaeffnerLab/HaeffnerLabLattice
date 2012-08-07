import numpy
numpy.seterr(divide='raise')
from scipy.interpolate import interp1d

class Interpolator():
    '''helper class for interpolating between x and y'''
    def __init__(self, x, y, t = 'cubic'):
        self.f = interp1d(x,y,kind = 'cubic')
        self.domain = (x.min(),x.max())
        
    def interpolated(self, x):
        if not numpy.logical_and(self.domain[0] <= x, x <= self.domain[1]).all(): raise Exception ("Trying to extrapolate outside the domain")
        return self.f(x)