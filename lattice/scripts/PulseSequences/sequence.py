class Sequence():
    def __init__(self, pulser):
        self.pulser = pulser
        self.vars = {}

    def setVariables(self, **input):
        #make sure no extraneous keys
        requiredKeys = self.requiredVars.keys()
        for key in input.keys():
            if key not in requiredKeys: raise Exception ("Provided key {} is not required by the sequence".format(key))
        #assign keys
        for name in self.requiredVars.keys():
            if name in input.keys():
                value = input[name]
            else:
                value = self.requiredVars[name][3]
            #error checking
            if type(value) != self.requiredVars[name][0]: raise Exception ('Wrong type for variable {}'.format(name))
            if not (self.requiredVars[name][1] <=  value <= self.requiredVars[name][2]): raise Exception ('Out of allowed range: {}'.format(name))
            self.vars[name] = value
        
    def defineSequence(self):
        pass