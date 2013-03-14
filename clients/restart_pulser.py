import labrad
import time

pulser_node = 'node_lattice_control'
pulser_name = 'Pulser'
errors = False

try:
	cxn = labrad.connect()
except:
	raise Exception( 'Please start LabRAD Manager')
else:
	#connected
	if pulser_node not in cxn.servers:
		raise Exception( '{} is not running'.format(pulser_node)) 
	else:
		cxn.servers[pulser_node].refresh_servers()
		running_servers = cxn.servers[pulser_node].running_servers().asarray
		if pulser_name not in running_servers: 
			raise Exception( '{} is not running'.format(pulser_name)) 
		dds_state = {}
		pulser = cxn.servers[pulser_name]
		for dds_channel in pulser.get_dds_channels():
			channel_state = [pulser.frequency(dds_channel), pulser.amplitude(dds_channel) , pulser.output(dds_channel)]
			print 'initial setting', channel_state
			dds_state[dds_channel] = channel_state
		line_trig_state = pulser.line_trigger_state()
		print 'restarting pulser'
		cxn.servers[pulser_node].restart(pulser_name)
		print 'done'
		time.sleep(1.0)
		cxn.refresh()
		pulser = cxn.servers[pulser_name]
		for channel, (freq, ampl, output) in dds_state.iteritems():
			print 'setting', channel, freq, ampl, output
			[pulser.frequency(channel, freq), pulser.amplitude(channel, ampl) , pulser.output(channel, output)]
		pulser.line_trigger_state(line_trig_state)