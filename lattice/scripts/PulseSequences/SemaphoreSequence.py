from labrad import types as T

class SemaphoreSequence(object):
	
	def __init__(self, semaphore, start = 0, **kwargs):
		self.start = start
		self.end = start
		self.sem = semaphore
		self.dds_pulses = []
		self.ttl_pulses = []
		self.replace = kwargs
		config = {}
		semP = self.set_semaphore_params(semaphore, self.semaphore_configuration() , **kwargs)
		userP = self.set_user_params(self.user_configuration() , **kwargs)
		config.update(semP)
		config.update(userP)
		self.p = Bunch(**config) 
		self.sequence()
		
	def semaphore_configuration(self):
		'''implemented by subclass'''	
		return {}
	
	def user_configuration(self):
		'''implemented by subclass'''	
		return {}		
	
	def sequence(self):
		'''implemented by subclass'''
	
	def set_semaphore_params(self, sem, params, **replace):
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
		return d
	
	def set_user_params(self, params, **replace):
		d = {}
		for param in params.iterkeys():
			minim,maxim,val = params[param]
			units = minim.units
			if param in replace.keys():
				val = replace[param].inUnitsOf(units)
			if not ((minim.value <= val.value) and (val.value <= maxim.value)):
				raise Exception ("Parameter {} is out of range".format(param))
			d[param] = val
		return d
	
	def addSequence(self, sequence, position = None, **kwargs):
		'''insert a subsequence, position is either time or None to insert at the end'''
		#position where sequence is inserted
		if type(position) == dict: raise Exception ("Don't forget ** in front of replacement dictionary")
		if position is None:
			position = self.end
		#replacement conists of global replacement and key work arguments
		replacement = {}
		replacement.update(self.replace)
		replacement.update(kwargs)
		print 'position',position
		seq = sequence(self.sem, start = position, **replacement)
		self.dds_pulses.extend( seq.dds_pulses )
		self.ttl_pulses.extend( seq.ttl_pulses )
		self.end = max(self.end, seq.end)
		
class Bunch:
	def __init__(self, **kwds):
		self.__dict__.update(kwds)
	
	def __setitem__(self, key, val):
		self.__dict__[key] = val
	
	def toDict(self):
		return self.__dict__