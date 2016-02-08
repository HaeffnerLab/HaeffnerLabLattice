from base_excitation import base_excitation

class molmer_sorensen_gate(base_excitation):
    from lattice.scripts.PulseSequences.molmer_sorensen_gate import ms_gate
    name = 'MolmerSorensenGate'
    pulse_sequence = ms_gate

class szx_gate(base_excitation):
    from lattice.scripts.PulseSequences.szx_1ion import szx_1ion
    name = 'SZXGate'
    pulse_sequence = szx_1ion

class szx_rabi(base_excitation):
    from lattice.scripts.PulseSequences.szx_rabi import szx_rabi as szxr
    name = 'SZXRabiFlop'
    pulse_sequence = szxr

class vaet(base_excitation):
    from lattice.scripts.PulseSequences.vaet_interaction import vaet_interaction as v
    name = 'VAET'
    pulse_sequence = v
    
class parity_flop(base_excitation):
    from lattice.scripts.PulseSequences.vaet_parity_flop import vaet_parity_flop as v
    name = 'ParityFlop'
    pulse_sequence = v
