#This Simple Measurement records timetags for a certain duration
import labrad
import time
from labrad.units import WithUnit
import numpy
from scripts.PulseSequences.subsequences.RecordTimeTags import record_timetags as sequence
#parameters
iterations = 2000
iteration_duration = WithUnit(0.20, 's')
#connect to servers
cxn = labrad.connect()
pulser = cxn.pulser
dv = cxn.data_vault
#set up saving
localtime = time.localtime()
datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
directory = ['','SimpleMeasurements','Timetags']
directory.extend(dirappend)
dv.cd(directory, True)
dv.new('Timetags {}'.format(datasetNameAppend),[('Iterations', 'Arb')],[('Timetags','sec','sec')] )

#program pulser
sequence_parameters = {'record_timetags_duration':iteration_duration}
seq = sequence(**sequence_parameters)
seq.programSequence(pulser)

print directory

for itr in range(iterations):
    pulser.start_number(1)
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    timetags = pulser.get_timetags().asarray
    print 'Got {} timetags'.format(timetags.size)
    iters = numpy.ones_like(timetags) * itr
    dv.add(numpy.vstack((iters, timetags)).transpose())
print 'DONE'