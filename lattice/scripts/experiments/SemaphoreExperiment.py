import numpy

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    
    def __setitem__(self, key, val):
        self.__dict__[key] = val
    
    def toDict(self):
        return self.__dict__
    
class SemaphoreExperiment():
    '''class with useful methods while running a semaphore experiment'''
    
    
    def populate_experimental_parameters(self, sem, path):
        '''return a bunch with all of the parameters in the given path'''
        d = {}
        path = list(path)
        params = sem.get_parameter_names(path)
        for param in params:
            path.append(param)
            d[param] = sem.get_parameter(path)
            path.pop()
        return Bunch(**d)
    
    def populate_global_parameters(self, sem, path):
        '''returns a bunch with all of the parameters higher in the tree than the given path'''
        d = {}
        path = list(path[:-1]) #exclude top directory
        current_path = []
        while True:
            try:
                current_path.append( path.pop(0) )
            except IndexError:
                return Bunch(**d)
            else:
                available_parameters = sem.get_parameter_names(current_path)
                for p in available_parameters:
                    current_path.append(p)
                    d[p] = sem.get_parameter(current_path)
                    current_path.pop()
    
    def check_parameters(self, entry, units = None):
        '''checks the ranges of parameters'''
        assert len(entry) >= 3, "Trying to check parameters that do not have enough entries"
        entry= list(entry)        
        minim,maxim =[entry.pop(0).inUnitsOf(units).value for i in range(2)]
        values = numpy.array([val.inUnitsOf(units).value for val in entry])
        withinRange = (minim <= values) * (values <= maxim)
        if not (withinRange.all()):
            raise Exception ("Some entries are out of range in {}".format(entry))
        return values

    def check_parameter(self, entry, units = None):
        '''checks the ranges of parameters'''
        assert len(entry) == 3, "Trying to check parameter that does not have enough entries"
        entry= list(entry)        
        minim,maxim,value =[entry.pop(0).inUnitsOf(units).value for i in range(3)]
        if not ((minim <= value) and (value <= maxim)):
            raise Exception ("Some entries are out of range in {}".format(entry))
        return value