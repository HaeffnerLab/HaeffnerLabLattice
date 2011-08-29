import labrad
import time

cxn = labrad.connect()

dv = cxn.data_vault
gpib = cxn.toshibalaptop_gpib_bus
scopename = gpib.list_devices()[0]
gpib.address(scopename)

dv.cd('QuickMeasurements',True)
dv.new('Cavity Temperature PID',[('time','sec')],[('errorSignal','errorSignal','V'),('PIDresponse','PIDresponse','V')])



while True:
    errorSignal = 
    
    scope = cxn.servers(
    scope.measure(1))
    
    PIDoutput = gpib.query('MEASurement:MEAS2:VALue?')
    t = time.time()
    time.sleep(0.1)
    dv.add([t,errorSignal,PIDoutput])
    print t
    print errorSignal
    print PIDoutput