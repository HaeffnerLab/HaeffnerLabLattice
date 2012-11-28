from twisted.internet import protocol

class ExperimentProtocol(protocol.ProcessProtocol):

    def __init__(self, name):
        self.name = name
    
    def connectionMade(self):
        print 'connection made:', self.transport.pid
    
    def processExited(self, reason):
        failure =  reason.value
        print 'error', failure.exitCode
    
    def childDataReceived(self, childFD, data):
        print 'child data Received', childFD
        print 'my name is', self.name
        print data.rstrip('\n')
        print 'over'

    def outReceived(self, data):
        print 'out received', self.name, data, 'over'


from twisted.internet import reactor
prot = ExperimentProtocol('one')

def rename():
    prot.name = 'two'
#-u enable line buffering
reactor.spawnProcess(prot, 'python', ['python','-u', '/Users/micramm/Documents/LabRAD/lattice/devel/ScriptLauncher/experiment.py',],
                     )
#                     childFDs = { 0: 0, 1: 1, 2: 2})

reactor.callLater(2, rename)
reactor.run()