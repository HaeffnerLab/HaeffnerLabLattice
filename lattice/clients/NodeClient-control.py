import labrad
import numpy as np
import time

nodeDict = {'node_lattice_control':
					['Serial Server','Data Vault', 'DAC', 'Compensation Box','Pulser',
					'Agilent Server', 'GPIB Device Manager', 'RohdeSchwarz Server','Tektronix Server','NormalPMTFlow',
					'Compensation LineScan','ADCserver',  'Trap Drive', 'HighVoltA','Semaphore'],
		}

#connect to LabRAD
errors = False
try:
	cxn = labrad.connect()
except:
	print 'Please start LabRAD Manager'
	errors = True
else:
	nodes = nodeDict.keys()
	if not len(nodes):
		print "No Nodes Running"
		errors = True
	for node in nodeDict.keys():
		#make sure all node servers are up
		if not node in cxn.servers:'{} is not running'.format(node)
		else:
			print '\nWorking on {} \n '.format(node)
			cxn.servers[node].refresh_servers()
			#if node server is up, start all possible servers on it that are not already running
			running_servers = np.array(cxn.servers[node].running_servers().asarray)
			for server in nodeDict[node]:
				if server in running_servers: 
					print server + ' is already running'
				else:
					print 'starting ' + server
					try:
						cxn.servers[node].start(server)
					except Exception as e:
						print 'ERROR with ' + server
						errors = True
	
if errors:
	time.sleep(10)