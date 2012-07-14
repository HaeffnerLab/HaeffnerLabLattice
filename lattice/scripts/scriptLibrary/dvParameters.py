def saveParameters(dv, dict):
    """Save the parameters from the dictionary dict into datavault"""
    for name in dict.keys():
        dv.add_parameter(name, dict[name])
        
def measureParameters(cxn, cxnlab, list):
    """Measures parameters in the list and returns the dictionary containing these"""
    dict = {}
    for item in list:
        if item == 'trapdrive':
            server = cxn.trap_drive
            dict['rffreq'] = server.frequency()
            dict['rfpower'] = server.amplitude()
        elif item == 'endcaps':
            server = cxn.dac
            dict['endcap1'] = server.get_voltage('endcap1')
            dict['endcap2'] = server.get_voltage('endcap2')
        elif item == 'compensation':
            server = cxn.compensation_box
            [comp1, comp2] = [server.getcomp(1), server.getcomp(2)]
            dict['comp1'] = comp1
            dict['comp2'] = comp2
        elif item == 'dcoffsetonrf':
            server = cxn.dac
            dict['dconrf1'] = server.get_voltage('dconrf1')
            dict['dconrf2'] = server.get_voltage('dconrf2')
        elif item == 'cavity397':
            server = cxnlab.laserdac
            dict['cavity397'] = server.getvoltage('397')
        elif item == 'cavity866':
            server = cxnlab.laserdac
            dict['cavity866'] = server.getvoltage('866')
        elif item == 'multiplexer397':
            server = cxnlab.multiplexer_server
            dict['frequency397'] = server.get_frequency('397')
        elif item == 'multiplexer866':
            server = cxnlab.multiplexer_server
            dict['frequency866'] = server.get_frequency('866')
        elif item == 'pulser':
            dict['timetag_resolution'] = cxn.pulser.get_timetag_resolution()
    return dict