import time
import numpy as np
from labrad.units import WithUnit

def setup_data_vault(cxn, context, args, plotLive = True):
    
    dv = cxn.data_vault
    
    output_size = args['output_size']
    name = args['experiment_name']
    window_name = [args['window_name']]
    dataset_name = args['dataset_name']
    
    localtime = time.localtime()
    datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
    dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
    directory = ['','Experiments']
    directory.extend([name])
    directory.extend(dirappend)
    dv.cd(directory ,True, context = context)
    dependents = [('Excitation','Ion {}'.format(ion),'Probability') for ion in range(output_size)]
    dv.new(dataset_name + ' {}'.format(datasetNameAppend),[('Excitation', 'us')], dependents , context = context)
    dv.add_parameter('Window', window_name, context = context)
    dv.add_parameter('plotLive', plotLive, context = context)
    
def simple_scan(parameter, unit):
    minim,maxim,steps = parameter
    minim = minim[unit]; maxim = maxim[unit]
    scan = np.linspace(minim,maxim, steps)
    scan = [WithUnit(pt, unit) for pt in scan]
    return scan