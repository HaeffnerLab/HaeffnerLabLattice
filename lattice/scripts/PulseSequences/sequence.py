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
            if type(value) != self.requiredVars[name][0]: raise Exception ('Wrong type for variable {}'.format(name))
            if not (self.requiredVars[name][1] <=  value <= self.requiredVars[name][2]): raise Exception ('Out of allowed range: {}'.format(name))
            self.vars[name] = value
        #create a helper class for keeping track of variables
        self.parameters = Bunch(**self.vars)
        
    def defineSequence(self):
        pass