def addDataVaultParameters(modpower, endcap1, endcap2, rffreq, rfpower, pmtint, c1min, c1max, c1steps, c2min, c2max, c2steps, modmin, modmax, modsteps, comment=''):
    from lrexp.lr import Client
    data_vault = Client.connection.data_vault
    
    data_vault.add_parameter('modulation power', modpower)
    data_vault.add_parameter('endcap voltages', [endcap1,endcap2])
    data_vault.add_parameter('rf freq', rffreq)
    data_vault.add_parameter('rf power', rfpower)
    data_vault.add_parameter('pmt integration steps', str(pmtint))
    data_vault.add_parameter('compensation 1 voltage scan', (c1min,c1max,c1steps))
    data_vault.add_parameter('compensation 2 voltage scan', (c2min,c2max,c2steps))
    data_vault.add_parameter('modulation frequency scan', (modmin, modmax, modsteps))
    data_vault.add_parameter('comment', comment)
    

def setFreqgetCounts(freq,pmtint):
    from lrexp.lr import Client
    import numpy
    
    cxn = Client.connection
    modSigGen = cxn.lattice_pc_agilent_33220a_server
    pmt = cxn.pmt_server
    modSigGen.setfreq(freq)
    modSigGen.setstate( 1 ) #turn on modulation
    arr = numpy.array( pmt.getnextreadings( pmtint ) )
    dataModOn = numpy.average( numpy.transpose(arr)[1] )
    modSigGen.setstate( 0 ) #turn off modulation
    arr = numpy.array( pmt.getnextreadings( pmtint ) )
    dataModOff = numpy.average( numpy.transpose(arr)[1] )
    normDiff = (dataModOn-dataModOff)/(dataModOn + dataModOff)
    
    return (dataModOn, dataModOff, normDiff )

def saveCompensationResult(c1,c2,freq,resultTuple):
    from lrexp.lr import Client
    data_vault = Client.connection.data_vault
    data_vault.add(c1,c2,freq,*resultTuple)

def ReSelectMiltiplexerChannels(prevSelected):
    from lrexp.lr import Client
    m = Client.connection.multiplexer_server
    numch = len(m.get_exposures())
    for chan in range(numch):
        if chan in prevSelected:
            m.toggle_channel(chan,True)
        else:
            m.toggle_channel(chan,False)

def wait(sleeptime):
    import time
    time.sleep(sleeptime)
    
