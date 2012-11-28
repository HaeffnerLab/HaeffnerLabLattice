import labrad
from labrad.wrappers import connectAsync
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor


max_signals = 100
signal_id = 99901
counter = 0
@inlineCallbacks
def connect():
    def printSignal(x,y):
        global counter
        print x,y
        if counter >= max_signals:
            reactor.stop()
        counter += 1
        
    cxn = yield connectAsync()
    server = yield cxn.trap_drive
    yield server.signal__settings_updated(signal_id)
    yield server.addListener(listener = printSignal, source = None, ID = signal_id)
    yield server.removeListener(listener = printSignal, source = None, ID = signal_id)
    print 'now listening'
reactor.callWhenRunning(connect)
reactor.run()