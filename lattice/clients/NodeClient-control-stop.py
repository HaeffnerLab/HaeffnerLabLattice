import labrad

#connect to LabRAD
errors = False
try:
	cxn = labrad.connect()
except:
	print 'Please start LabRAD Manager'
	errors = True
else:
	
	for node in ['node_lattice_control']:
		#make sure all node servers are up
		if not node in cxn.servers:'{} is not running'.format(node)
		else:
			print '\nWorking on {} \n '.format(node)
			cxn.servers[node].refresh_servers()
			#if node server is up, start all possible servers on it that are not already running
			running_servers = cxn.servers[node].running_servers()
			for name, othername in running_servers:
				print 'stopping {}'.format(name)
				cxn.servers[node].stop(name)