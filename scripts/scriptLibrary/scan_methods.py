import time
import numpy as np
from labrad.units import WithUnit

def setup_data_vault(cxn, context, args, plotLive = True):

    '''
    Datavault setup function for standard experiments.

    Creates a datavault structure with the layout:
    Experiments/Year_Month_Day/timetag

    Experiment type is saved as a parameter
    associated with the dataset

    cxn: LabRAD connecction object
    context: LabRAD context object
    plotLive: set True if data should be live plotted

    args: dictionary of parameters with the values:
    scan_type: string labeling the type of scan, e.g. spectrum729
    headings: list of strings labeling each column in the datasets, e.g, ['ion 0', 'ion 1', 'ion 2']
    axis (optional): x-axis range
    send_to_current (optional): send data to 'current' plot in grapher
    '''
    
    dv = cxn.data_vault
    
    scan_type = args['scan_type']
    headings = args['headings']
    try:
        send_to_current = args['send_to_current']
    except:
        send_to_current = True
    localtime = time.localtime()
    timetag = time.strftime("%H%M_%S", localtime)
    directory = ['','Experiments', time.strftime('%Y_%m_%d', localtime), timetag] # data is in $datadir/Experiments/Y_M_D/timetag
    dv.cd(directory ,True, context = context)
    dependents = [('arb',label,'arb') for label in headings]
    ds =  dv.new(timetag, [('arb', 'arb')], dependents , context = context)
    if plotLive:
        window_name = args['window_name']
        try:
            axis = args['axis']
            cxn.grapher.plot_with_axis(ds, window_name, axis, send_to_current)     
        except:
            cxn.grapher.plot(ds, window_name, send_to_current)
    dv.add_parameter('scan_type', scan_type, context = context)

def setup_data_vault_appendable(cxn, context, name, headings):
    '''
    Datavault setup function for continuous measurements,
    e.g. drift tracking data compiled continuously throughout the day.
    Stores datasets in the directory:
    Experiments/Year_Month_Day/continuous

    cxn: LabRAD connection object
    context: LabRAD context object
    name: string with the dataset name, e.g. 'ramsey line 1'
    headings: list of strings labeling each column in the dataset, e.g, ['average', 'deviation']
    '''
    
    dv = cxn.data_vault
    
    localtime = time.localtime()
    directory = ['','Experiments', time.strftime('%Y_%m_%d', localtime), 'continuous']
    dv.cd(directory, True, context = context)
    try:
        dv.open_appendable('00001 - ' + name, context = context) # datavault appends a leading string with dataset number
    except: # dataset does not exist
        dependents = [('arb',label,'arb') for label in headings]
        ds = dv.new( name, [('arb', 'arb')], depdendents, context = context)
        

def simple_scan(parameter, unit, offset = None):
    minim,maxim,steps = parameter
    minim = minim[unit]; maxim = maxim[unit]
    if offset is not None:
        minim += offset[unit]
        maxim += offset[unit]
        
    scan = np.linspace(minim,maxim, steps)
    scan = [WithUnit(pt, unit) for pt in scan]
    return scan
