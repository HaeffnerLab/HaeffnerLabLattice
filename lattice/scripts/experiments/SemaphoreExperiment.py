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
    
    def populate_parameters(self, sem, path):
        '''
        Returns a bunch with all of the parameters
        Repeated names are overwritten, with directories further down in the tree given priority
        '''
        d = {}
        path = list(path) #exclude top directory
        current_path = []
        while True:
            available_parameters = sem.get_parameter_names(current_path)
            for p in available_parameters:
                current_path.append(p)
                if p in d: print "Warning, overwriting parameter {}".format(p)
                d[p] = sem.get_parameter(current_path)
                current_path.pop()          
            try:
                current_path.append( path.pop(0) )
            except IndexError:
                return Bunch(**d)

    def check_parameters(self, entry, units = None, keep_units = False):
        '''checks the ranges of parameters'''
        assert len(entry) >= 3, "Trying to check parameters that do not have enough entries"
        entry= list(entry)        
        minim,maxim =[entry.pop(0).inUnitsOf(units).value for i in range(2)]
        if not keep_units:
            values =[val.inUnitsOf(units).value for val in entry]
        else:
            values = [val.inUnitsOf(units) for val in entry]
        values_np = numpy.array(values) #automatically gets rid of units
        withinRange = (minim <= values_np) * (values_np <= maxim)
        if not (withinRange.all()):
            raise Exception ("Some entries are out of range in {}".format(entry))
        return values

    def check_parameter(self, entry, units = None, keep_units = False):
        '''checks the ranges of parameters'''
        assert len(entry) == 3, "Trying to check parameter that does not have enough entries"
        entry= list(entry)
        minim,maxim,value =[entry.pop(0).inUnitsOf(units) for i in range(3)]
        if not ((minim.value <= value.value) and (value.value <= maxim.value)):
            raise Exception ("Some entries are out of range in {}".format(entry))
        if not keep_units:
            return value.value
        else:
            return value