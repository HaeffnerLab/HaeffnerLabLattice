import  labrad

cxn = labrad.connect()
sc = cxn.scriptscanner
dv = cxn.data_vault

def get_data(ds):
    direc, dset = ds[0]
    dv.cd(direc)
    dv.open(dset)
    return dv.get()

# modify new_sequence to take a list of override parameters

scan = [('RabiFlopping',   ('RabiFlopping.duration', 0., 50.0, 5.0, 'us'))]

ident = sc.new_sequence('RabiFlopping', scan)
print "scheduled the sequence"
sc.sequence_completed(ident) # wait until sequence is completed
ds = sc.get_dataset(ident) # needs to be implemented
x = get_data(ds)
print x
cxn.disconnect()