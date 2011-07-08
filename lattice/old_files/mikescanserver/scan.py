class Repeat():
    def __init__(self,action,numIter):
	self.numIter = numIter
	self.action = action
	
    def listParameters(self):
	return self.action.listParameters()

    def setParameter(self,name,value):
	self.action.setParameter(name,value)
	
    def execute(self):
	for self.iter in range(self.numIter):
	    self.action.execute()
	
class OneDScan():
    def __init__(self,action,parameter,xmin,xmax,numSteps):
	self.action = action
	self.parameter = parameter
	self.xmin = xmin
	self.xmax = xmax
	self.numSteps = numSteps
	self.delta = (self.xmax - self.xmin)/float(self.numSteps-1)
	
    def listParameters(self):
	return self.action.listParameters()
	
    def setParameter(self,name,value):
	self.action.setParameter(name,value)
	
    def execute(self):
	for currentStep in range(self.numSteps):
	    currentValue = self.xmin + currentStep*self.delta
	    self.action.setParameter(self.parameter, currentValue)
	    self.action.execute()

class TwoDScan(OneDScan):
    def __init__(self,action,(xparameter,yparameter),(xmin,ymin),(xmax,ymax),(xNumSteps,yNumSteps)):
	self.action = action
	BottomScan = OneDScan(self.action,xparameter,xmin,xmax,xNumSteps)
	self.TopScan = OneDScan(BottomScan,yparameter,ymin,ymax,yNumSteps)
	
    def listParameters(self):
	return self.action.listParameters()
	
    def setParameter(self,name,value):
	self.action.setParameter(name,value)
	
    def execute(self):
	self.TopScan.execute()
	
class Sequence():
    def __init__(self,actionList):
	self.actionList = actionList
	self.availableParameters,self.parameterMap = self._getParameters()

    def _getParameters(self):
	availableParameters = []
	parameterMap = {}
	for action in self.actionList:
	    actionParams = action.listParameters()
	    for parameter in actionParams:
		# if some parameter already appears, this means that two actions share the same parameter name
		if availableParameters.count(parameter) > 0:
		    print 'WARNING, non-unique parameter name among two actions in a sequence'
		availableParameters.append(parameter)
		parameterMap[parameter]=action
	return availableParameters,parameterMap
	
    def setParameter(self,name,value):
	action = self.parameterMap[name]
	action.setParameter(name,value)

    def execute(self):
	for action in self.actionList:
	    action.execute()
		    	
    def listParameters(self):
	return self.availableParameters

    def setParameter(self,name,value):
	action = self.parameterMap[name]
	action.setParameter(name,value)

    def execute(self):
	for action in self.actionList:
	    action.execute()
	
	
#EVERYTHING IS AN ACTION!
#everything inherits action?
#object Action implements setParameter(), and execute(), listParameters()
#do some checking to make sure parametes are fine    
	

	    
	  
