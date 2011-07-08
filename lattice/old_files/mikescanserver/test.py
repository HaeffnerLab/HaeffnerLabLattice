class Action():
    def __init__(self):
	self.d = {
	    'one': 0,
	    'two': 0,
	    }
	    
    def listParameters(self):
	return self.d.keys()

    def setParameter(self,name,value):
	self.d[name]= value
	
    def execute(self):
	print 'action is to print',self.d['one'],self.d['two']
	
class ActionB():
    def __init__(self):
	self.d = {
	    'a': 0,
	    'b': 0,
	    }
	    
    def listParameters(self):
	return self.d.keys()

    def setParameter(self,name,value):
	self.d[name]= value
	
    def execute(self):
	print 'actionB ',self.d['a'],self.d['b']