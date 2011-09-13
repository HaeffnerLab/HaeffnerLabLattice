def addParametersCavityDacCalibration(cavitychannel, scanrange, comment=''):
    from lrexp.lr import Client
    data_vault = Client.connection.data_vault
    
    data_vault.add_parameter('cavity channel', cavitychannel)
    data_vault.add_parameter('scan range', scanrange)
    data_vault.add_parameter('comment', comment)

def addParametersLineScanCavity(cavitychannel, scanrange, pmtint, comment=''):
    from lrexp.lr import Client
    data_vault = Client.connection.data_vault
    laserdac = Client.connection.laserdac
    multiplexer_server = Client.connection.multiplexer_server
    dc_box = Client.connection.dc_box
    comp_box = Client.connection.compensation_box
    lattice_pc_hp_server = Client.connection.lattice_pc_hp_server
    #provided parameters
    data_vault.add_parameter('scanning cavity channel', cavitychannel)
    data_vault.add_parameter('scan range', scanrange)
    data_vault.add_parameter('pmt integration steps', pmtint)
    data_vault.add_parameter('comment', comment)
    #external parameters: cavity, frequency
    [init866, init397] = [laserdac.getcavity(ch) for ch in ['866','397']]
    [ch866, ch397] = [multiplexer_server.get_channel_from_wavelength(ch) for ch in ['866','397']]
    [freq866,freq397] = [multiplexer_server.get_frequency(ch) for ch in [ch866,ch397]]
    data_vault.add_parameter('initial 866 cavity',init866)
    data_vault.add_parameter('initial 866 frequency',freq866)
    data_vault.add_parameter('initial 397 cavity',init397)
    data_vault.add_parameter('initial 397 frequency',freq397)
    #external parameters: voltages, RF
    [endcap1,endcap2] = [dc_box.getendcap(ch) for ch in [1,2]]
    data_vault.add_parameter('endcap voltages', [endcap1,endcap2])
    [comp1, comp2] = [comp_box.getcomp(1), comp_box.getcomp(2)]
    data_vault.add_parameter('high volt compensation voltages', [comp1,comp2])
    rffreq = lattice_pc_hp_server.getfreq()
    rfpower = lattice_pc_hp_server.getpower()
    data_vault.add_parameter('rf freq', rffreq)
    data_vault.add_parameter('rf power', rfpower)