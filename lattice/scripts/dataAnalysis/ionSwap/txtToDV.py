import numpy as np
import labrad

numKin = 300
      
cxn = labrad.connect()
server = cxn.andor_ion_count

diskPath = ('C:\\Users\\lattice\\Documents\\Andor\\jun12\\062812\\7\\image')

server.open_as_text_kinetic(diskPath, 1, numKin)

dvPath = str(['', 'Experiments', 'IonSwap', '2012Jun28', '2012Jun28_7777_77', 'Scans'])

server.save_to_data_vault_kinetic(dvPath, ('Kinetic Set - 7'), 300)

print 'done!'


