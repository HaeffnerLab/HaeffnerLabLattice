def saveParameters(dv, d):
    """Save the parameters from the dictionary dict into datavault"""
    for name in d.keys():
        dv.add_parameter(name, d[name])
        
def measureParameters(cxn, cxnlab, specified = None):
    """Measures parameters in the list and returns the dictionary containing these"""
    d = {}
    local = {
#            'trapdrive':measure_trapdrive,
            'endcaps':measure_endcaps,
            'compensation':measure_compensation,
#            'dcoffsetonrf':measure_dcoffsetonrf,
            }
    lab = {
            'cavity397':measure_cavity('397'),
            'cavity866':measure_cavity('866'),
            'multiplexer397':measure_multiplexer('397'),
            'multiplexer397':measure_multiplexer('866'),
           }
    for setting,connection in [(local, cxn),(lab,cxnlab)]:
        if specified is None:
            for name in setting.keys():
                measure = setting[name]
                try:
                    measure(connection, d)
                except Exception, e:
                    print 'Unable to Measure {0}'.format(name), e
        else:
            raise NotImplementedError
    return d

def measure_trapdrive(cxn, d):
    server = cxn.trap_drive
    d['rffreq'] = server.frequency()
    d['rfpower'] = server.amplitude()

def measure_endcaps(cxn , d):
    server = cxn.dac
    d['endcap1'] = server.get_voltage('endcap1')
    d['endcap2'] = server.get_voltage('endcap2')
    
def measure_compensation(cxn , d):
    server = cxn.dac
    d['comp1'] = server.get_voltage('comp1')
    d['comp2'] = server.get_voltage('comp2')
    
def measure_dcoffsetonrf(cxn , d):
    server = cxn.dac
    d['dconrf1'] = server.get_voltage('dconrf1')
    d['dconrf2'] = server.get_voltage('dconrf2')

def measure_cavity(wavelegnth):
    def func(cxnlab ,d):
        server = cxnlab.laserdac
        d['cavity{}'.format(wavelegnth)] = server.getvoltage(wavelegnth)
    return func

def measure_multiplexer(wavelegnth):
    def func(cxnlab ,d):
        server = cxnlab.multiplexer_server
        d['multiplexer{}'.format(wavelegnth)] = server.get_frequency(wavelegnth)
    return func