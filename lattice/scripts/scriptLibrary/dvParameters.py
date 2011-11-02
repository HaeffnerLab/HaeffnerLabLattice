def saveParameters(dv, dict):
    """Save the parameters from the dictionary dict into datavault"""
    for name in dict.keys():
        dv.add_parameter(name, dict[name])
        
def measureParameters(cxn, list):
    """Measures parameters in the list and returns the dictionary containing these"""
    dict = {}
    for item in list:
        if item == 'trapdrive':
            server = cxn.lattice_pc_hp_server
            dict['rffreq'] = cxn.lattice_pc_hp_server.getfreq()
            dict['rfpower'] = cxn.lattice_pc_hp_server.getpower()
        elif item == 'endcaps':
            server = cxn.dc_box
            [endcap1,endcap2] = [server.getendcap(ch) for ch in [1,2]]
            dict['endcap1'] = endcap1
            dict['endcap2'] = endcap2
        elif item == 'compensation':
            server = cxn.compensation_box
            [comp1, comp2] = [server.getcomp(1), server.getcomp(2)]
            dict['comp1'] = endcap1
            dict['comp2'] = endcap2
        elif item == 'dcoffsetonrf':
            server = cxn.dc_box
            dict['dcoffsetonrf'] = server.getdcoffsetrf()
        elif item == 'cavity397':
            server = cxn.laserdac
            dict['cavity397'] = server.getvoltage('397')
        elif item == 'cavity866':
            server = cxn.laserdac
            dict['cavity866'] = server.getvoltage('866')
        elif item == 'multiplexer397':
            server = cxn.multiplexer_server
            dict['frequency397'] = cxn.multiplexer_server.get_frequency('397')
        elif item == 'multiplexer866':
            server = cxn.multiplexer_server
            dict['frequency866'] = cxn.multiplexer_server.get_frequency('866')
        elif item == 'axialDP':
            server = cxn.double_pass
            server.select('axial')
            dict['frequency_axialDP'] = server.frequency()
            dict['power_axialDP'] = server.amplitude()
            dict['output_axialDP'] = server.output()
        elif item == 'radialDP':
            server = cxn.double_pass
            server.select('radial')
            dict['frequency_radialDP'] = server.frequency()
            dict['power_radialDP'] = server.amplitude()
            dict['output_radialDP'] = server.output()
    return dict