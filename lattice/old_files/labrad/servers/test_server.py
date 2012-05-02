# Copyright (C) 2007  Matthew Neeley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from labrad import types as T, util
from labrad.server import LabradServer, setting
from labrad.util import hydrant

from twisted.internet import defer, reactor
from twisted.internet.defer import inlineCallbacks, returnValue


class TestServer(LabradServer):
    """Server to test labrad from python.

    This server provides a number of settings that
    are useful for testing labrad code, network profiling,
    and testing the python labrad library.
    """
    name = 'Python Test Server'
    testMode = True
    shutdownMessage = 987654321

    @inlineCallbacks
    def initServer(self):
        from registry_wrapper_async import RegistryWrapperAsync
        self.regWrapper = yield RegistryWrapperAsync.create(self.client, ['', 'Servers', 'Python Test Server'])

    @inlineCallbacks
    def stopServer(self):
        print 'before yield'
        yield None
        print (yield self.client.manager.convert_units(T.Value(5, 'GHz'), 'Hz'))
        print 'after yield'

    def serverConnected(self, ID, name):
        print 'server connected:', ID, name
        self.checkServerWrappers(name)

    def serverDisconnected(self, ID, name):
        print 'server disconnected:', ID, name
        self.checkServerWrappers(name)
    
    @inlineCallbacks
    def checkServerWrappers(self, name):
        """Check that server wrappers are up to date with the manager."""
        mgrServers = yield self.client.manager.servers()
        mgrServers = set(s[1] for s in mgrServers)
        cxnServers = set(self.client.servers.keys())
        if cxnServers == mgrServers:
            print 'self.client updated for server', name
        else:
            print 'self.client not properly refreshed:'
            print '  servers that should be disconnected:', list(cxnServers - mgrServers)
            print '  servers that have not been connected:', list(mgrServers - cxnServers)
    
    def initContext(self, c):
        c['dict'] = {}
    
    @setting(2, "Delayed Echo")
    def delayed_echo(self, c, data):
        """Echo a packet after a specified delay."""
        yield util.wakeupCall(c['delay'])
        returnValue(data)

    @setting(3, "Delayed Echo Deferred")
    def delayed_echo_deferred(self, c, data):
        """Echo a packet after a specified delay."""
        d = defer.Deferred()
        reactor.callLater(c['delay'], d.callback, data)
        return d

    @setting(4, "Echo Delay", delay=['v[s]', ''], returns=['v[s]'])
    def echo_delay(self, c, delay):
        """Get or set the echo delay."""
        self.log('Echo delay: %s' % delay)
        if delay is not None:
            c['delay'] = float(delay)
        return c['delay']

    @setting(40, "Speed", speed=['v[m/s]', ''], returns=['v[m/s]'])
    def speed(self, c, speed):
        """Get or set the speed."""
        self.log('Speed: %s' % speed)
        if speed is not None:
            c['speed'] = speed
        return c['speed']

    @setting(41, "Verbose Echo")
    def verbose_echo(self, c, data):
        print type(data)
        print repr(data)
        return data

    @setting(5, "Exc in Handler")
    def exc_in_handler(self, c, data):
        """Raises an exception directly in the handler."""
        self.log('Exception in handler.')
        raise Exception('Raised in handler.')

    @setting(6, "Exc in Subfunction")
    def exc_in_subfunction(self, c, data):
        """Raises an exception in a subfunction."""
        self.log('Exception in subfunction.')
        owie()

    @setting(7, "Exc in Deferred")
    def exc_in_deferred(self, c, data):
        """Returns a deferred that fires an exception."""
        self.log('Exception in deferred.')
        d = defer.Deferred()
        d.addCallback(owie)
        reactor.callLater(1, d.callback, None)
        return d

    @setting(8, "Exc in Errback")
    def exc_in_errback(self, c, data):
        """Returns a deferred whose errback will be called."""
        self.log('Exception from an errback.')
        d = defer.Deferred()
        reactor.callLater(1, d.errback, Exception('Raised by errback.'))
        return d

    @setting(9, "Exc in inlineCallback")
    def exc_in_inlinecallback(self, c, data):
        """Raises an exception in an inlineCallback."""
        self.log('Exception from an inlineCallback.')
        yield util.wakeupCall(c['delay'])
        raise Exception('Raised in inlineCallback.')

    @setting(10, "Bad Return Type", returns=['s'])
    def bad_return_type(self, c, data):
        """Returns a value that does not match the declared return type."""
        return 5
        
    @setting(11, "Get Random Data", tag=['s'])
    def get_random_data(self, c, tag=None):
        """Get a random bit of data conforming to the specified type tag."""
        if tag is None:
            t = hydrant.randType()
        else:
            t = T.parseTypeTag(tag)
        return hydrant.randValue(t)
        
    @setting(12, "Get Random Tag")
    def get_random_tag(self, c, tag):
        """Get a random LabRAD type tag."""
        return str(hydrant.randType())

    @setting(100, "Set", key='s', value='?', returns='')
    def set(self, c, key, value):
        c['dict'][key] = value
    
    @setting(101, "Get", key='s', returns='?')
    def get(self, c, key):
        return c['dict'][key]
    
    @setting(102, "Keys", returns='*s')
    def keys(self, c):
        return sorted(c['dict'].keys())

def owie(dummy=None):
    raise Exception('Raised in subfunction.')
        
__server__ = TestServer()

if __name__ == '__main__':
    util.runServer(__server__)
