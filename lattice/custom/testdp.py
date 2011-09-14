import labrad
import numpy
cxn = labrad.connect()
dp = cxn.dataprocessor
print dp.get_available_processes()
dp.set_inputs('timeResolvedBinning',[('timelength',1000),('resolution',5),('bintime',100)])
dp.new_process('timeResolvedBinning')
fakedata = numpy.array([[0,255],[2,255]])
dp.process_new_data('timeResolvedBinning',fakedata)
print dp.get_result('timeResolvedBinning').asarray