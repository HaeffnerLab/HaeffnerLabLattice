from labrad.units import WithUnit

'''
Methods for setting up the single pass AOMs
'''

def setup_sp_global(dds_cw, args):
    
    f_global = WithUnit(80.0, 'MHz') + WithUnit(0.15, 'MHz')
    
    bichro_shift = args['bichro_shift']
    try:
        detuning = args['detuning']
    except:
        detuning = WithUnit(0, 'MHz')
    try:
        ac_stark_shift = args['ac_stark_shift']
    except:
        ac_stark_shift = WithUnit(0, 'MHz')
    freq_blue = f_global - bichro_shift - detuning + ac_stark_shift
    freq_red = f_global + bichro_shift + detuning + ac_stark_shift
    
    amp_red = args['amp_red']
    amp_blue = args['amp_blue']
    
    dds_cw.frequency('0', freq_blue)
    dds_cw.frequency('1', freq_red)
    dds_cw.frequency('2', f_global) # for driving the carrier
    dds_cw.amplitude('0', amp_blue)
    dds_cw.amplitude('1', amp_red)
    dds_cw.output('0', True)
    dds_cw.output('1', True)
    dds_cw.output('2', True)
        
def setup_sp_local(dds_cw, args):
    f_local = WithUnit(80.0, 'MHz') - WithUnit(0.2, 'MHz')
    bichro_shift = args['bichro_shift']
    try:
        detuning = args['detuning']
    except:
        detuning = WithUnit(0, 'MHz')
    try:
        ac_stark_shift = args['ac_stark_shift']
    except:
        ac_stark_shift = WithUnit(0, 'MHz')
    freq_blue = f_local - bichro_shift - detuning + ac_stark_shift
    freq_red = f_local + bichro_shift + ac_stark_shift
    
    amp_red = args['amp_red']
    amp_blue = args['amp_blue']
    
    dds_cw.frequency('3', freq_blue)
    dds_cw.frequency('4', freq_red)
    dds_cw.frequency('5', f_local) # for driving the carrier
    dds_cw.amplitude('3', amp_blue)
    dds_cw.amplitude('4', amp_red)
    dds_cw.output('3', True)
    dds_cw.output('4', True)
    dds_cw.output('5', True)
