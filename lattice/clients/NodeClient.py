import labrad
import numpy as np
import time
cxn = labrad.connect()

try:
	lpcnode = cxn.node_lattice_pc
except:
	print 'Not all node servers running.'
	time.sleep(2)
	raise()


running_servers = np.array(lpcnode.running_servers().asarray)

#available: 'RS Server blue','HighVoltA','HighVoltB','Agilent Server','Compensation Box'

serverstostart = ['Data Vault','Serial Server','DC Box','HP Server',
				'RS Server red','PMT server','Direct Ethernet','Time Resolved Server']


for server in serverstostart:
	if server not in running_servers:
		print 'Lattice-pc: trying to start', server
		lpcnode.start(server)
		#lpcnode.stream_output(server, True) ###doesn't do anythin for seom reason
		print 'Lattice-pc node: started', server
	else:
		print 'Lattice-pc node:', server, ' already running'	

try:
	pbnode = cxn.node_paul_s_box
except:
	print 'Not all node servers running.'
	time.sleep(2)
	raise()

serverstostart = ['Paul Box']
running_servers = np.array(pbnode.running_servers().asarray)

for server in serverstostart:
	if server not in running_servers:
		print 'Pauls Box node trying to start', server
		pbnode.start(server)
		print 'Pauls Box node: started', server
	else:
		print 'Pauls Box node:', server, ' already running'	

try:
	lab49node = cxn.node_lab_49
except:
	print 'Not all node servers running.'
	time.sleep(2)
	raise()

serverstostart = ['Serial Server','LaserDAC']
running_servers = np.array(lab49node.running_servers().asarray)

for server in serverstostart:
	if server not in running_servers:
		print 'Lab-49 node trying to start', server
		lab49node.start(server)
		print 'Lab-49 node: started', server
	else:
		print 'Lab-49 node:', server, ' already running'	


print 'ALL DONE'
time.sleep(2)