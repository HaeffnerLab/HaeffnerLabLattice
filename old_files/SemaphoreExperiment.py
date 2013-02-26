import numpy

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    
    def __setitem__(self, key, val):
        self.__dict__[key] = val
        
    def iteritems(self):
        return self.__dict__.iteritems()
    
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

    def check_parameters(self, entry, keep_units = True, in_units = None):
        '''checks the ranges of parameters'''
        assert len(entry) >= 3, "Trying to check parameters that do not have enough entries"
        entry= list(entry)        
        minim,maxim =[entry.pop(0).value for i in range(2)]
        values =[val for val in entry]
        #assumes the units are the same for the min,max,and values
        values_np = numpy.array(values) #automatically gets rid of units
        withinRange = (minim <= values_np) * (values_np <= maxim)
        if not (withinRange.all()):
            raise Exception ("Some entries are out of range in the list {}".format(values_np))
        if not keep_units:
            #discard units
            if in_units is None:
                in_units = minim.units
            return [val.inUnitsOf(in_units).value for val in values]
        else:
            return values

    def check_parameter(self, entry, keep_units = True, in_units = None):
        '''checks the ranges of parameters'''
        if type(entry) == bool: return entry #nothing to check
        assert len(entry) == 3, "Trying to check parameter that does not have enough entries"
        entry= list(entry)
        minim,maxim,value =[entry.pop(0) for i in range(3)]
        #assumes the units are the same for the min,max,and value
        if not ((minim.value <= value.value) and (value.value <= maxim.value)):
            raise Exception ("Entry {2} must be in between {0} and {1}".format(minim, maxim, value))
        if not keep_units:
            #discard units
            if in_units is None:
                in_units = minim.units
            return value.inUnitsOf(in_units).value
        else:
            return value