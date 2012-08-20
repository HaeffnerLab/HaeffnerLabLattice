from labrad import types as T

class PulseSequence(object):
	
	def __init__(self, start = T.Value(0, 's'), **kwargs):
		self.start = start
		self.end = start
		self.dds_pulses = []
		self.ttl_pulses = []
		self.added_sequences = []
		self.replace = kwargs
		config = self.set_params(self.configuration() , **kwargs)
		self.p = Bunch(**config) 
		self.sequence()
	
	@staticmethod
	def configuration():
		'''implemented by subclass'''	
		return []
	
	@staticmethod
	def needs_subsequences():
		'''implement by subclass'''
		return []
	
	def sequence(self):
		'''implemented by subclass'''
	
	def set_params(self, params, **replace):
		d = {}
		for param in params:
			try:
				d[param] = replace[param]
			except KeyError:
				raise Exception('{0} value not provided for the {1} Pulse Sequence'.format(param, self.__class__.__name__))
		return d
	
	def addSequence(self, sequence, position = None, **kwargs):
		'''insert a subsequence, position is either time or None to insert at the end'''
		#position where sequence is inserted
		if sequence not in self.needs_subsequences(): raise Exception ("Adding sequence that is not listed in the 'needs_subsequences' method")
		if type(position) == dict: raise Exception ("Don't forget ** in front of replacement dictionary")
		if position is None:
			position = self.end
		#replacement conists of global replacement and key work arguments
		replacement = {}
		replacement.update(self.replace)
		replacement.update(kwargs)
		seq = sequence(start = position, **replacement)
		self.dds_pulses.extend( seq.dds_pulses )
		self.ttl_pulses.extend( seq.ttl_pulses )
		self.end = max(self.end, seq.end)
		self.added_sequences.append(sequence)
	
	@classmethod
	def requiredParameters(cls, returnDict = False):
		'''returns a set (or optically a dictionary) of the required parameters'''
		required = set(cls.configuration())
		for seq in cls.needs_subsequences():
			required = required.union(seq.requiredParameters())
		if returnDict:
			required = {}.fromkeys(required)
		return required
		
class Bunch:
	def __init__(self, **kwds):
		self.__dict__.update(kwds)
	
	def __setitem__(self, key, val):
		self.__dict__[key] = val
	
	def toDict(self):
		return self.__dict__