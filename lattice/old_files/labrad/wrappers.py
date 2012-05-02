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

from __future__ import absolute_import

import functools
from types import MethodType
from collections import defaultdict

from twisted.internet import defer
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.python.components import registerAdapter

from zope.interface import implements

from labrad import constants as C, protocol
from labrad.interfaces import ILabradProtocol, ILabradManager, IClientAsync
from labrad.util import mangle, MultiDict, extractKey


class AsyncSettingWrapper(object):
    """Represents a setting on a remote LabRAD server."""
    
    def __init__(self, server, name, pyName, ID, info):
        self.name = self.__name__ = self._labrad_name = name
        self._py_name = pyName
        self._updateInfo(ID, info)
        self._server = server
        self._cxn = server._cxn
        self._prot = server._cxn._cxn
        self._num_listeners = 0

    def _updateInfo(self, ID, info):
        """Update meta information about this setting."""
        self.ID = ID
        self.__doc__, self.accepts, self.returns, self.notes = info

    def __call__(self, *args, **kw):
        """Send a request to this setting."""
        tag = extractKey(kw, 'tag', None) or self.accepts
        if len(args) == 0:
            args = None
        elif len(args) == 1:
            args = args[0]
        d = self._server._send([(self.ID, args, tag)], **kw)
        d.addCallback(lambda r: r[0][1])
        return d
    
    @inlineCallbacks
    def connect(self, handler, context=(0, 0),
                connectargs=(), connectkw={},
                handlerargs=(), handlerkw={}):
        """Connect a handler to messages from this signal.
        
        This is only applicable if the remote setting handles
        signal connection and disconnection.  We also keep
        track of the number of handlers that have been added to
        this setting.
        """
        self._prot.addListener(handler,
                               source=self._server.ID, context=context, ID=self.ID,
                               args=handlerargs, kw=handlerkw)
        self._num_listeners += 1
        try:
            yield self.__call__(self.ID, context=context, *connectargs, **connectkw)
        except:
            self._prot.removeListener(handler,
                                      source=self._server.ID, context=context, ID=self.ID)
            self._num_listeners -= 1
            raise
    
    def disconnect(self, handler, context=(0, 0),
                   disconnectargs=(), disconnectkw={}):
        """Disconnect a handler for messages from this signal.
        
        If the number of handlers drops to zero, we make a request to
        tell the signal to stop sending us messages.
        """
        self._prot.removeListener(handler, source=self._server.ID, context=context, ID=self.ID)
        self._num_listeners = max(self._num_listeners - 1, 0)
        return self.__call__(context=context, *disconnectargs, **disconnectkw)     

class SettingBinder(object):
    """A dictionary proxy that binds methods to an instance.
    
    This is used to emulate the old 'settings' attribute on a packet
    wrapper, now that the settings have been moved into a class.
    """
    # TODO fill out dict functionality here (.keys(), .items(), etc.)
    def __init__(self, inst):
        self._inst = inst
    
    def __getitem__(self, key):
        inst = self._inst
        return inst._bind(inst.__class__.settings[key])

class AsyncPacketWrapper(object):
    """Represents a LabRAD packet to a server.
    
    One wrapper class is created for each server.  Settings can be added or
    removed from the wrapper class as needed, if the server settings change.
    """

    @classmethod
    def _addSetting(cls, setting):
        """Add a new instance method for the specified setting.
        
        Instance methods are cached, so that if a setting goes away and
        comes back later, the method will still point back to the
        same setting object.
        """
        if setting.name in cls._cache:
            method = cls._cache[setting.name]
        else:
            def wrapped(self, *args, **kw):
                key = extractKey(kw, 'key', None)
                tag = extractKey(kw, 'tag', None) or setting.accepts
                if len(args) == 0:
                    args = None
                elif len(args) == 1:
                    args = args[0]
                self._packet.append((setting.ID, args, tag, key))
                return self
            wrapped.name = setting.name
            method = MethodType(wrapped, None, cls)
        cls._cache[setting.name] = method
        cls.settings[setting.name, setting._py_name, setting.ID] = method
        setattr(cls, setting._py_name, method)
    
    @classmethod
    def _refreshSetting(cls, setting):
        """Refresh a setting by updating its aliases in our setting MultiDict."""
        cls.settings._updateAliases(setting.name, setting._py_name, setting.ID)
    
    @classmethod
    def _delSetting(cls, setting):
        """Delete the instance method for the specified setting."""
        del cls.settings[setting.name]
        delattr(cls, setting._py_name)


    def __init__(self, **kw):
        """Create a new packet."""
        self._packet = []
        self._kw = kw
        self.settings = SettingBinder(self)

    def send(self, **kw):
        """Send this packet to the server."""
        # drop keys from records before sending
        records = [rec[:3] for rec in self._packet]
        d = self._server._send(records, **dict(self._kw, **kw))
        d.addCallback(PacketResponse, self._server, self._packet)
        return d

    def _bind(self, method):
        """Bind a method to this instance."""
        return functools.partial(method, self)
    
    def __getitem__(self, key):
        """Get a setting method from the class and bind it to this instance."""
        return self._bind(self.__class__.settings[key])

    def __setitem__(self, key, value):
        """Update existing parts of the packet, indexed by key.
        
        Note that if multiple records share the same key, they will
        all be updated.
        """
        for i, rec in enumerate(self._packet):
            if key == rec[3]:
                self._packet[i] = rec[0], value, rec[2], rec[3]
    
    def __delitem__(self, key):
        """Delete a setting call from this packet, indexed by key.
        
        Note that if multiple records share the same key, they will
        all be deleted.
        """
        for i, rec in enumerate(self._packet):
            if key == rec[3]:
                self._packet.pop(i)
        
    # TODO implement flattened versions of packet object to allow for packet forwarding
    #def __lrtype__(self):
    #    pass
    
    #def __lrflatten__(self):
    #    pass

def makePacketWrapperClass(server):
    """Make a new packet wrapper class for a particular server."""
    class CustomPacketWrapper(AsyncPacketWrapper):
        settings = MultiDict()
        _server = server
        _cache = {}
    return CustomPacketWrapper
    

class AsyncServerWrapper(object):
    """Represents a remote LabRAD server."""
    
    def __init__(self, cxn, name, pyName, ID):
        self._cxn = cxn
        self._mgr = cxn._mgr
        self.name = self._labrad_name = name
        self._py_name = pyName
        self.ID = ID
        self.settings = MultiDict()
        self._cache = {}
        self._packetWrapperClass = makePacketWrapperClass(self)
        self._refreshLock = defer.DeferredLock()

    def refresh(self):
        return self._refreshLock.run(self._refresh)

    @inlineCallbacks
    def _refresh(self):
        """Update the list of available settings for this server."""

        # get info about this server and its settings
        info = yield self._mgr.getServerInfoWithSettings(self.ID)
        self.__doc__, self.notes, settings = info
        names = [s[0] for s in settings]

        # determine what to add, update and delete to be current
        for s in settings:
            if s[0] not in self.settings:
                self._addSetting(*s)
            else:
                self._refreshSetting(*s)
        for n in self.settings:
            if n not in names:
                self._delSetting(n)
        
    _staticAttrs = ['settings', 'refresh', 'context', 'packet',
                    'sendMessage', 'addListener', 'removeListener']
    
    def _fixName(self, name):
        pyName = mangle(name)
        if pyName in self._staticAttrs:
            pyName = 'lr_' + pyName
        return pyName

    def _addSetting(self, name, ID, info):
        """Add a wrapper for a new setting for this server.
        
        The wrapper will be pulled from the cache and reused if
        one has already been created for a setting with this name.
        Also add this setting to the packet wrapper class.
        """
        if name in self._cache:
            setting = self._cache[name]
            setting._updateInfo(ID, info)
        else:
            pyName = self._fixName(name)
            setting = AsyncSettingWrapper(self, name, pyName, ID, info)
            self._cache[name] = setting
        self.settings[name, setting._py_name, ID] = setting
        setattr(self, setting._py_name, setting)
        # also add to the packet class
        self._packetWrapperClass._addSetting(setting)

    def _refreshSetting(self, name, ID, info):
        """Refresh the info about a particular setting.
        
        In particular, update the MultiDict mapping if the
        setting ID has changed.
        """
        setting = self.settings[name]
        aliasChanged = (ID != setting.ID)
        setting._updateInfo(ID, info)
        if aliasChanged:
            # update aliases if the ID has changed
            self.settings._updateAliases(name, setting._py_name, ID)
            self._packetWrapperClass._refreshSetting(setting)

    def _delSetting(self, name):
        """Remove the wrapper for a setting."""
        setting = self.settings[name]
        del self.settings[name]
        delattr(self, setting._py_name)
        # also remove from the packet class
        self._packetWrapperClass._delSetting(setting)

    def context(self):
        """Create a new context for talking to this server."""
        return self._cxn.context()

    def packet(self, **kw):
        """Create a new packet for this server."""
        return self._packetWrapperClass(**kw)

    def sendMessage(self, ID, *args, **kw):
        """Send a message to this server."""
        tag = extractKey(kw, 'tag', [])
        if len(args) == 0:
            args = None
        elif len(args) == 1:
            args = args[0]
        self._cxn._sendMessage(self.ID, [(ID, args, tag)], **kw)
    
    def addListener(self, listener, **kw):
        """Add a listener for messages from this server."""
        kw['source'] = self.ID
        self._cxn._addListener(listener, **kw)
        
    def removeListener(self, listener, **kw):
        """Remove a listener for messages from this server."""
        kw['source'] = self.ID
        self._cxn._removeListener(listener, **kw)
        
    def __call__(self):
        return self
        # TODO this should make a clone that can have different
        # default keyword args, and, in particular, should talk
        # to the server in a different context

    def __getitem__(self, key):
        return self.settings[key]

    def _send(self, *args, **kw):
        """Send packet to this server."""
        return self._cxn._send(self.ID, *args, **kw)

@inlineCallbacks
def getConnection(host=C.MANAGER_HOST, port=C.MANAGER_PORT, name="Python Client", password=None):
    """Connect to LabRAD and return a deferred that fires the protocol object."""
    p = yield protocol.factory.connectTCP(host, port, C.TIMEOUT)
    if password is None:
        password = protocol.getPassword()
    yield p.loginClient(password, name)
    returnValue(p)

@inlineCallbacks
def connectAsync(host=C.MANAGER_HOST, port=C.MANAGER_PORT, name="Python Client", password=None):
    """Connect to LabRAD and return a deferred that fires the client object."""
    p = yield getConnection(host, port, name, password)
    cxn = IClientAsync(p)
    yield cxn._init()
    cxn.onDisconnect = p.onDisconnect
    returnValue(cxn)

def runAsync(func, *args, **kw):
    from twisted.internet import reactor
    @inlineCallbacks
    def runIt():
        try:
            yield func(*args, **kw)
        finally:
            reactor.stop()
    reactor.callWhenRunning(runIt)
    reactor.run()

class ClientAsync(object):
    """Adapt a LabRAD request protocol object to an asynchronous client."""
    
    implements(IClientAsync)
    
    def __init__(self, prot):
        self.servers = MultiDict()
        self._cache = {}
        self._cxn = prot
        self._mgr = ILabradManager(self._cxn)
        self._next_context = 1
        self._refreshLock = defer.DeferredLock()
        
    _staticAttrs = ['servers', 'refresh', 'context']

    @inlineCallbacks
    def _init(self):
        """Refresh the cache of available servers and their settings.
        
        Also set up messages so that servers that connect and disconnect later
        will be automatically detected, without needing a refresh.
        """
        try:
            yield self._mgr.subscribeToNamedMessage('Server Connect', 314159265, True)
            yield self._mgr.subscribeToNamedMessage('Server Disconnect', 314159266, True)
            self._cxn.addListener(self._serverConnected, source=self._mgr.ID, ID=314159265, async=False)
            self._cxn.addListener(self._serverDisconnected, source=self._mgr.ID, ID=314159266, async=False)
            yield self.refresh()
        except Exception, e:
            print 'error!'
            print repr(e)
            raise
            
    @inlineCallbacks
    def _serverConnected(self, c, data):
        """Add a wrapper when a server connects."""
        ID, name = data
        try:
            yield self._addServer(name, ID)
        except Exception, e:
            print 'Error adding server %d, "%s":' % (ID, name)
            print str(e)
        
    @inlineCallbacks
    def _serverDisconnected(self, c, data):
        """Remove the wrapper when a server disconnects."""
        ID, name = data
        try:
            yield self._delServer(name)
        except Exception, e:
            print 'Error removing server %d, "%s":' % (ID, name)
            print str(e)

    def refresh(self):
        return self._refreshLock.run(self._refresh)

    @inlineCallbacks
    def _refresh(self):
        """Update the list of available LabRAD servers."""
        
        # get a list of the currently-available servers
        slist = yield self._mgr.getServersList()
        names = [s[0] for s in slist]
        
        # determine what to add, update and delete to be current
        additions = [s for s in slist if s[0] not in self.servers]
        refreshes = [n for n in self.servers if n in names]
        deletions = [n for n in self.servers if n not in names]

        actions = ([self._addServer(*s) for s in additions] +
                   [self._refreshServer(n) for n in refreshes] +
                   [self._delServer(n) for n in deletions])
        yield defer.DeferredList(actions, fireOnOneErrback=True)

    def _fixName(self, name):
        pyName = mangle(name)
        if pyName in self._staticAttrs:
            pyName = 'lr_' + pyName
        return pyName

    @inlineCallbacks
    def _addServer(self, name, ID):
        """Create a wrapper for a new server and add it to the list.
        
        Wrappers are cached so that if a server stops and restarts,
        the old wrapper will be reused and references to it do not
        need to be updated.
        """
        if name in self._cache:
            # pull from cache if possible
            server = self._cache[name]
        else:
            # create a new wrapper and cache it
            pyName = self._fixName(name)
            server = AsyncServerWrapper(self, name, pyName, ID)
            self._cache[name] = server
        try:
            yield server.refresh()
        except Exception, e:
            print 'Error while refreshing server "%s":' % name
            print repr(e)
        else:
            self.servers[name, server._py_name, ID] = server
            setattr(self, server._py_name, server)

    @inlineCallbacks
    def _refreshServer(self, name):
        """Trigger a refresh on a server wrapper."""
        server = self.servers[name]
        try:
            yield server.refresh()
        except Exception, e:
            print 'Error while refreshing server "%s":' % name
            print repr(e)
            yield self._delServer(name)

    def _delServer(self, name):
        """Remove a server wrapper.
        
        The wrapper is kept in the cache, to be reused if this
        server ever comes back.
        """
        if name in self.servers:
            server = self.servers[name]
            del self.servers[name]
            delattr(self, server._py_name)
        return defer.succeed(None)

    def context(self):
        """Create a new communication context for this connection."""
        context = (0, self._next_context)
        self._next_context += 1
        return context

    def __getitem__(self, key):
        return self.servers[key]

    def _send(self, target, records, *args, **kw):
        """Send a packet over this connection."""
        return self._cxn.sendRequest(target, records, *args, **kw)
        
    def _sendMessage(self, target, records, *args, **kw):
        """Send a message over this connection."""
        return self._cxn.sendMessage(target, records, *args, **kw)
        
    def disconnect(self):
        self._cxn.disconnect()
        
    @property
    def _addListener(self):
        return self._cxn.addListener
    
    @property
    def _removeListener(self):
        return self._cxn.removeListener

registerAdapter(ClientAsync, ILabradProtocol, IClientAsync)

def wrapAsync(cls, *args, **kw):
    obj = cls(*args, **kw)
    d = obj.refresh()
    d.addCallback(lambda x: obj)
    return d


class PacketResponse(object):
    """Wrapper for response packets from LabRAD servers.

    Attributes are added to access the records in this
    response packet coming from each setting.  For each
    setting called by the packet, we add an attribute to
    access the response from that setting.  If a setting
    is called more than once, all responses from that setting
    are collected into a list.  Responses can be accessed
    by name or ID, unless a key was specified for the call,
    in which case the response is accessible via the key only.
    """
    def __init__(self, resp, server, packet):
        # collect all responses from each setting or key
        temp = defaultdict(list)
        for rec, (ID, data) in zip(packet, resp):
            key = rec[3]
            setting = server.settings[ID]
            name, pyName = setting.name, setting._py_name
            # if this record has a key, index by key only
            # otherwise by setting name, python name and ID
            if key is not None:
                name = pyName = ID = key
            keys = (name, pyName, ID)
            temp[keys].append(data)
        # add data for the various settings
        self.settings = MultiDict()
        for (name, pyName, ID), l in temp.items():
            if len(l) == 1:
                l = l[0]
            if isinstance(pyName, str):
                setattr(self, pyName, l)
            self.settings[name, pyName, ID] = l

    def __getitem__(self, key):
        return self.settings[key]

