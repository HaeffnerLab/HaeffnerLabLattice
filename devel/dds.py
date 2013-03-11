durationAdvance = 2 #duration of the 'adance' TTL pulse in pulser timesteps
minPulseLengthTTL = durationAdvance
minPulseLengthDDS = 2 * durationAdvance
minPulseGapOnFreqChange = 150 #timesteps, which is 6 microseconds

#defining pulse classes
class pulse(object):
    def __init__(self, channel, start, end):
        self.channel = channel
        self.start = start
        self.end = end

class dds_pulse(pulse):
    def __init__(self, channel, start, end, freq, ampl, phase = 0.0):
        super(dds_pulse, self).__init__(channel, start, end)
        self.pulse_type = 'dds'
        self.freq = freq
        self.ampl = ampl
        self.phase = phase
    
    @property
    def setting(self):
        return (self.freq, self.ampl, self.phase)

class ttl_pulse(pulse):
    def __init__(self, channel, start, end):
        super(ttl_pulse, self).__init__(channel, start, end)
        self.pulse_type = 'ttl'

def pulse_type_limits(pulse):
    '''
    returns the limits on duration for dds and tll pulses
    '''
    if pulse.pulse_type == 'dds':
        minPulseLength = minPulseLengthDDS
        minGapNoChange = minPulseLengthDDS
        minGapOnChange = (minPulseGapOnFreqChange, minPulseLengthDDS, minPulseLengthDDS)
    elif pulse.pulse_type == 'ttl':
        minPulseLength = minPulseLengthTTL
        minGapOnChange = minPulseLengthTTL
        minGapNoChange = (minPulseLengthTTL, )
    return minPulseLength, minGapOnChange, minGapNoChange

def check_errors(last_pulse, new_pulse):
    minPulseLength, minGapOnChange, minGapNoChange = pulse_type_limits(last_pulse)
    difference = new_pulse.start - last_pulse.end
    message_collision=''
    message_duration=''
    if difference < 0:
        message_collision = "Overlap found at {0} channel {1}. Pulse starting at {2} but previous ending at {3}"
    elif last_pulse.setting == new_pulse.setting and difference < minGapNoChange:
        message_collision = "Gap Between Pulses Too Short for {0} channel {1}. Pulse starting at {2} but previous ending at {3}"
    else:
        #check on errors if any of the settings were changed
        for i,last_setting in enumerate(last_pulse.setting):
            if new_pulse.setting[i] != last_setting and difference < minGapOnChange[i]:
                message_collision = "Gap Between Pulses Too Short for {0} channel {1}. Pulse starting at {2} but previous ending at {3}"
    #check for duration erros of each pulse
    for p in [last_pulse, new_pulse]:
        if p.start < minPulseLength:
            message_duration = "Pulse starts too early for {0} channel {1}, starting at {2}"
            message_duration = message_duration.format(p.pulse_type, p.channel, p.start)
        if p.end - p.start < minPulseLength:
            message_duration = "Pulse is too short for {0} channel {1}, starting at {2}, ending at {3}"
            message_duration = message_duration.format(p.pulse_type, p.channel, p.start, p.end)
    #format and raise the relevant error message
    message = '' 
    if message_collision:
        message = message_collision.format(new_pulse.pulse_type, new_pulse.channel, new_pulse.start, last_pulse.end)
    if message_duration:
        message = message_duration
    if message:
        raise Exception (message)

def merge_adjacent(pulse_list):
    '''
    merges adjacent dds pulses by combining pulses together when they are back to back and have the same dds settings
    '''
    merged = []
    pulses_sorted_by_start = sorted(pulse_list, key = lambda pulse: pulse.start)
    if not pulses_sorted_by_start: return merged
    last_pulse = pulses_sorted_by_start.pop(0)
    while pulses_sorted_by_start:
        pulse = pulses_sorted_by_start.pop(0)
        if last_pulse.end == pulse.start and last_pulse.setting == pulse.setting:
            last_pulse.end = pulse.end
        else:
            check_errors(last_pulse, pulse)
            merged.append(last_pulse)
            last_pulse = pulse
    merged.append(last_pulse)
    return merged


def get_merged_pulses():
    '''returns all pulses while mergent adjacent pulses for each channel'''
    all_pulses = []
    for pulse_list in d.itervalues():
        merged = merge_adjacent(pulse_list)
        all_pulses.extend(merged)
    return all_pulses

def parse_dds():
    '''
    state starts out in the initial state and then get updated by the pulse edges
    '''
    all_pulses = get_merged_pulses()
    for p in all_pulses:
        print p.start, p.end
    if not all_pulses: return None
#    state = self.parent._getCurrentDDS()
#    dds_program = {}.fromkeys(state, '')
#    pulses_sorted_by_start = sorted(all_pulses, key = lambda pulse: pulse.start)
#    pulse = pulses_sorted_by_start.pop(0)
#    last_start = pulse.start
#        while pulses_sorted_by_start:
#            
    
def add_to_dds_program(self, prog, state):
    for name,num in state.iteritems():
        if not hardwareConfiguration.ddsDict[name].remote:
            buf = self.parent._intToBuf(num)
        else:  
            buf = self.parent._intToBuf_remote(num)
        prog[name] += buf

    
d = {'729': []}
d['729'].append(dds_pulse('729DP', 5.0, 16.0, 220.0, -10.0))
d['729'].append(dds_pulse('729DP', 16.0, 25.0, 220.0, -10.0 ))
d['729'].append(dds_pulse('729DP', 175.0, 250.0, 221.0, -10.0))
    
parse_dds()