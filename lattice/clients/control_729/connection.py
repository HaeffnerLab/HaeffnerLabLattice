from twisted.internet.defer import inlineCallbacks

class connection(object):
    
    host='localhost'
    
    def __init__(self, cxn = None):
        self.cxn = cxn
    
    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            from labrad.wrappers import connectAsync
            self.cxn = yield connectAsync(self.host)
            print 'before dv'
            self.dv = yield self.cxn.data_vault
            print 'after dv'


if __name__ == '__main__':
    from twisted.internet import reactor
    app = connection()
    reactor.run()