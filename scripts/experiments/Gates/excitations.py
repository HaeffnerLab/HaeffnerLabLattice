from base_excitation import base_excitation

class molmer_sorensen_gate(base_excitation):
    from lattice.scripts.PulseSequences.molmer_sorensen_gate import ms_gate
    name = 'MolmerSorensenGate'
    pulse_sequence = ms_gate

class szx_gate(base_excitation):
    from lattice.scripts.PulseSequences.szx_1ion import szx_1ion
    name = 'SZXGate'
    pulse_sequence = szx_1ion
