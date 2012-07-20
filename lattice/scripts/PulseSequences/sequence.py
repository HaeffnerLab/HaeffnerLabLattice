class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class Sequence():
    def __init__(self, pulser):
        self.pulser = pulser
        self.vars = {}
        self.parameters = None

    def setVariables(self, **input):
        #make sure no extraneous keys
        requiredKeys = self.requiredVars.keys()
        for key in input.keys():
            if key not in requiredKeys: raise Exception ("Provided key {} is not required by the sequence".format(key))
        #assign keys
        for name in requiredKeys:
            if name in input.keys():
                value = input[name]
            else:
                value = self.requiredVars[name][3]
                print 'Assigning key {0} to the default value {1}'.format(name, value)
            #error checking
            okay = self.error_check(value,  self.requiredVars[name], name)
            if okay: 
                self.vars[name] = value
        #create a helper class for keeping track of variables
        self.parameters = Bunch(**self.vars)
    
    def error_check(self, value, required, name):
        if type(value) == list:
            #list error checking
            type_def = required[0]
            if not type_def[0] == list: raise Exception ("Not expected list for variable {}".format(name))
            element_type = type_def[1]
            for el in value:
                if type(el) != element_type: raise Exception ('Wrong type for variable {}'.format(name))
                if not (required[1] <=  el <= required[2]): raise Exception ('element {} out of allowed range: {}'.format(el, name))
        else:
            #non-list error checking 
            if type(value) != required[0]: raise Exception ('Wrong type for variable {}'.format(name))
            if not (required[1] <=  value <= required[2]): raise Exception ('Out of allowed range: {}'.format(name))
        return True
        
    def defineSequence(self):
        pass