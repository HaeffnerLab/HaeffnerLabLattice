class SemaphoreSequence(object):
	
	def __init__(self, semaphore, start = 0, **kwargs):
		self.start = start
		self.end = start
		self.sem = semaphore
		self.dds_pulses = []
		self.ttl_pulses = []
		self.replace = kwargs
		self.p = self.setParameters(semaphore, self.configuration(), **kwargs)
		self.sequence()
		
	def configuration(self):
		'''implemented by subclass'''	
		return {}
	
	def sequence(self):
		'''implemented by subclass'''
	
	def setParameters(self, sem, params, **replace):
		d = {}
		for param in params.iterkeys():
			path = params[param]
			minim,maxim,val = sem.get_parameter(path)
			units = minim.units
			if param in replace.keys():
				val = replace[param].inUnitsOf(units)
			if not ((minim.value <= val.value) and (val.value <= maxim.value)):
				raise Exception ("Parameter {} is out of range".format(param))
			d[param] = val
		return Bunch(**d)
	
	def addSequence(self, sequence):
		seq = sequence(self.sem, start = self.end, **self.replace)
		self.dds_pulses.extend( seq.dds_pulses )
		self.ttl_pulses.extend( seq.ttl_pulses )
		self.end = seq.end
		
		
	
class Bunch:
	def __init__(self, **kwds):
		self.__dict__.update(kwds)
	
	def __setitem__(self, key, val):
		self.__dict__[key] = val
	
	def toDict(self):
		return self.__dict__