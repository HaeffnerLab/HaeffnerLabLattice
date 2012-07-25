import labrad
from labrad.types import Error
cxn = labrad.connect()
flow = cxn.normalpmtflow

NotFoundError
print cxn.random
#try:
#    flow.set_save_folder([''])
#except Error("") as err:
#    if err.code == 5:
#        print 'failing'

#flow.set_save_folder([''])
        