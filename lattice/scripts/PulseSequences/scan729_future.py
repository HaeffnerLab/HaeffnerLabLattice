class Sequence():
    def __init__(self, **args):
        self.pos = 0
        self.dur = 0
        self.pulse_list = []
        self.set(args)
        
    def set(self, **args):
        pass
    
    def add(self, sequences):
        for seq in sequences:
            pulses = seq.pulses()
            duration = seq.duration()
            self.pos += duration
            self.pulse_list.extend(pulses)
    
    def duration(self):
        return self.dur
    
    def pulses(self):
        return []
    
class RepumpD(Sequence):
    def set(self, args):
        self.freq = args.get('freq', 80)
        self.dur = 100
    
    def pulses(self):
        self.pulses = [(0, self.freq, -3), (100, self.freq, -63)]
        
        return self.pulses

class DopplerCooling(Sequence):
            
    def set(self, args):
        self.freq = args.get('freq', 110)
        self.dur = 100
        
    def pulses(self):
        self.pulses = [(0, self.freq, -3), (100, self.freq, -63)]
        
        return self.pulses
    
    
class FrequencyScan(Sequence):
    
    def set(self, args):
        pass
    
    def pulses(self):
        operations = [
                    DopplerCooling(),
                    RepumpD(),
                    ]
        self.add(operations)
        return self.pulses()

freqs = [220.0,210.0, 22.0]
sequence = DopplerCooling()
print sequence.pulses()
sequence = RepumpD()
print sequence.pulses()
sequence = FrequencyScan()
print sequence.pulses()


