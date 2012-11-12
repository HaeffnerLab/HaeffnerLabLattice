class config(object):
    
    #dictionary in the form semaphore_path: (import_part, name)
    ExperimentInfo = {
     ('Test', 'Exp1'):  ('clients.guiscriptcontrol.experiments.Test', 'Test'),
     ('Test', 'Exp2'):  ('clients.guiscriptcontrol.experiments.Test2', 'Test2'),
     ('Test', 'Exp3'):  ('clients.guiscriptcontrol.experiments.Test3', 'Test3'),
     ('SimpleMeasurements', 'ADCPowerMonitor'):  ('scripts.simpleMeasurements.ADCpowerMonitor', 'ADCPowerMonitor'),
     ('729Experiments','Spectrum'):  ('scripts.experiments.Experiments729.spectrum', 'spectrum'),
     ('729Experiments','RabiFlopping'):  ('scripts.experiments.Experiments729.rabi_flopping', 'rabi_flopping'),
     ('729Experiments','BlueHeating'):  ('scripts.experiments.Experiments729.blue_heating_rabi_flopping', 'blue_heating_rabi_flopping'),
     ('BranchingRatio',):  ('scripts.experiments.BranchingRatio.branching_ratio', 'branching_ratio')
     }
    
    
    #conflicting experiments, every experiment conflicts with itself
    conflictingExperiments = {
    ('Test', 'Exp1'): [('Test', 'Exp1'), ('Test', 'Exp2')],
    ('Test', 'Exp2'): [('Test', 'Exp2')],
    ('Test', 'Exp3'): [('Test', 'Exp3')],
    ('SimpleMeasurements', 'ADCPowerMonitor'):  [('SimpleMeasurements', 'ADCPowerMonitor')],
    ('729Experiments','Spectrum'):  [('729Experiments','Spectrum')],
    ('729Experiments','RabiFlopping'):  [('729Experiments','RabiFlopping')],
    ('729Experiments','BlueHeating'):[('729Experiments','BlueHeating')],
    ('BranchingRatio',):[('BranchingRatio',)]
    }