
top_directory = ['','Experiments','RabiFlopping','2013Sep04']

def list_parameters(cxn):
    dv = cxn.data_vault
    dv.cd(top_directory)
    directories = dv.dir()[0]
    for direct in sorted(directories):
        dv.cd(top_directory)
        dv.cd(direct)
        dv.open(1)
        parameters = dict(dv.get_parameters())
        try:
            param = parameters['Heating.background_heating_time']
            print direct, param
        except KeyError:
            print direct, None







import labrad
with labrad.connect() as cxn:
    list_parameters(cxn)