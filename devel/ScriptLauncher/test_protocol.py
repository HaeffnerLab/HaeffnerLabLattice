from twisted.internet import protocol
from twisted.internet.defer import Deferred

class ExperimentProtocol(protocol.ProcessProtocol):
    '''
    Protocol for running an experimental script
    
    @var self.on_exit: a Deferred which will be calledback when the process exits. True on error-free completion, False otherwise.
    '''

    def __init__(self, name):
        self.name = name
        self.on_exit = Deferred()
    
    def connectionMade(self):
        print '{0} started'.format(self.name)
    
    def processEnded(self, reason):
        '''
        called when the process is ended
        '''
        failure = reason.value
        code = failure.exitCode
        if not code:
            print '{0} finished with no errors'.format(self.name)
            self.on_exit.callback(True)
        else:
            print '{0} finished with an error'.format(self.name)
            self.on_exit.callback(False)
    
    def outReceived(self, data):
        '''
        print the stdout from the running process
        '''
        print '{0}: {1}'.format(self.name, data.rstrip('\n'))
    
    def errReceived(self, data):
        '''
        print the errout from the running process
        '''
        print 'ERROR in {0}: {1}'.format(self.name, data.rstrip('\n'))
    
    def kill(self):
        '''
        kills the process
        '''
        self.transport.signalProcess('KILL')

from twisted.internet import reactor

def finished(a):
    print 'finished', a

protocol = ExperimentProtocol('experiment_name')
on_protocol_exit = protocol.on_exit
on_protocol_exit.addCallback(finished)
#-u enable line buffering
reactor.spawnProcess(protocol, 'python', ['python','-u', '/Users/micramm/Documents/LabRAD/lattice/devel/ScriptLauncher/experiment.py',])

reactor.run()