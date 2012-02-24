import labrad
cxn = labrad.connect()
pulser = cxn.pulser
pulser.new_sequence()
duration = 1
for i in range(8):
    pulser.add_ttl_pulse(str(i),  i * duration, duration)
pulser.program_sequence()
pulser.start_infinite()
#pulser.start()
print pulser.human_readable().asarray