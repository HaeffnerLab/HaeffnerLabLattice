import labrad
cxn = labrad.connect()
pulser = cxn.pulser
pulser.new_sequence()
pulser.add_ttl_pulse('testChannel', start = 0, duration = 1)
pulser.add_ttl_pulse('testChannel', start = 2, duration = 1)
pulser.program_sequence()
pulser.start_infinite()
#
#buf1 = "\x00\x00\x00\x00\x00\x00\x01\x00"
#buf2 = "\x20\x00\x00\x00\x00\x00\x02\x00"
#buf3 = "\x40\x00\x00\x00\x00\x00\x04\x00"