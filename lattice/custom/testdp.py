import labrad
cxn = labrad.connect()
dp = cxn.dataprocessor
print dp.get_available_processes()
dp.set_inputs('timeResolvedBinning',[('timelength',0.100),('resolution',5*10**-9),('bintime',100*10**-6)])
dp.new_process('timeResolvedBinning')
print dp.get_result('timeResolvedBinning').asarray.shape
print dp.get_result('timeResolvedBinning').asarray[0:5]