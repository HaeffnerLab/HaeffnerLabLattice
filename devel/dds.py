import numpy as np
#check for pulse overalap
#duration is positive
#start time reasonable
#need certain space for duration and between pulses

durationAdvance = 2
minPulseLength = 2 * durationAdvance 

class dds_pulse(object):
    def __init__(self, channel, start, end, setting):
        self.channel = channel
        self.start = start
        self.end = end
        self.setting = setting

d = {'729': []}
d['729'].append(dds_pulse('729DP', 5.0, 12.0, 5))
d['729'].append(dds_pulse('729DP', 16.0, 20.0, 10))
d['729'].append(dds_pulse('729DP', 20.0, 30.0, 10))

def check_collision_errors(last_pulse, new_pulse):
    if last_pulse.end > new_pulse.start:
            message = "Overlap found at channel {0}. Pulse starting at {1} but previous ending at {2}"
            message = message.format(new_pulse.channel, new_pulse.start, last_pulse.end)
            raise Exception (message)
    elif last_pulse.end + minPulseLength > new_pulse.start:
            message = "Time between consecutive pulses too short channel {0}. Pulse starting at {1} but previous ending at {2}"
            message = message.format(new_pulse.channel, new_pulse.start, last_pulse.end)
            raise Exception (message)

def check_duration_errors(pulse):
    if pulse.start < minPulseLength:
        message = "Pulse starts too early for channel {0}, starting at {1}"
        message = message.format(pulse.channel, pulse.start)
        raise Exception (message)
    if pulse.end - pulse.start < minPulseLength:
        message = "Pulse is too short for channel {0}, starting at {1}, ending at {2}"
        message = message.format(pulse.channel, pulse.start, pulse.end)
        raise Exception (message)

def merge_adjacent_dds(pulse_list):
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
            check_collision_errors(last_pulse, pulse)
            check_duration_errors(last_pulse)
            merged.append(last_pulse)
            last_pulse = pulse
    merged.append(last_pulse)
    return merged

def get_all_pulses():
    all_pulses = []
    for pulse_list in d.itervalues():
        merged = merge_adjacent_dds(pulse_list)
        all_pulses.extend(merged)
    return all_pulses

def parse_dds():
    '''
    state starts out in the initial state and then get updated by the pulse edges
    '''
    all_pulses = get_all_pulses()
    if not all_pulses: return None
    state = self.parent._getCurrentDDS()
    dds_program = {}.fromkeys(state, '')
    pulses_sorted_by_start = sorted(all_pulses, key = lambda pulse: pulse.start)
    pulse = pulses_sorted_by_start.pop(0)
    last_start = pulse.start
        while pulses_sorted_by_start:
            
    
    
def add_to_dds_program(self, prog, state):
    for name,num in state.iteritems():
        if not hardwareConfiguration.ddsDict[name].remote:
            buf = self.parent._intToBuf(num)
        else:  
            buf = self.parent._intToBuf_remote(num)
        prog[name] += buf
    
parse_dds()
        