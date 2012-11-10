from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtCore

class Parameter(object):
    def __init__(self, path, setValue, updateSignal, setRange = None, units = ''):
        self.path = path
        self.setValue = setValue
        self.setRange = setRange
        self.updateSignal = updateSignal
        self.units = units

class async_semaphore(object):
    '''class containig useful methods for asynchornous iteraction with the semaphore'''
    
    @inlineCallbacks
    def connect_labrad(self):
        from labrad.units import WithUnit
        from labrad.types import FlatteningError
        self.FlatteningError = FlatteningError
        self.WithUnit = WithUnit
        if self.cxn is None:
            from connection import connection
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            yield self.subscribe_semaphore()
        except Exception, e:
            print e
            self.setDisabled(True)
        self.cxn.on_connect['Semaphore'].append( self.reinitialize_semaphore)
        self.cxn.on_disconnect['Semaphore'].append( self.disable)
        self.connect_widgets_labrad()
        
    @inlineCallbacks
    def disable(self):
        self.setDisabled(True)
        yield None
    
    @inlineCallbacks
    def subscribe_semaphore(self): 
        yield self.cxn.servers['Semaphore'].signal__parameter_change(self.semaphoreID, context = self.context)
        yield self.cxn.servers['Semaphore'].addListener(listener = self.on_parameter_change, source = None, ID = self.semaphoreID, context = self.context)
        for path,param in self.d.iteritems():
            path = list(path)
            init_val = yield self.cxn.servers['Semaphore'].get_parameter(path, context = self.context)
            self.set_value(param, init_val)
        self.subscribed = True
    
    def on_parameter_change(self, x, y):
        path, init_val = y
        path = path.astuple
        if path in self.d.keys():
            param = self.d[path]
            self.set_value(param, init_val)
    
    @inlineCallbacks
    def reinitialize_semaphore(self):
        self.setDisabled(False)
        yield self.cxn.servers['Semaphore'].signal__parameter_change(self.semaphoreID, context = self.context)
        if not self.subscribed:
            yield self.cxn.servers['Semaphore'].addListener(listener = self.on_parameter_change, source = None, ID = self.semaphoreID, context = self.context)
            for path,param in self.d.iteritems():
                path = list(path)
                init_val = yield self.cxn.servers['Semaphore'].get_parameter(path, context = self.context)
                self.set_value(param, init_val)
            self.subscribed = True
    
    def connect_widgets_labrad(self):
        for params in self.d.itervalues():
            try:
                params.updateSignal.connect(self.set_labrad_parameter(params.path, params.units))
            except AttributeError:
                for p in params:
                    p.updateSignal.connect(self.set_labrad_parameter(p.path, p.units))
                
    def set_value(self, param, val):
        if type(val) == bool:
            param.setValue(val)
        else:
            try:
                newval = [v.inUnitsOf(param.units) for v in val]
                val = newval
            except:
                #if unitless number
                pass
            r_min,r_max = val[0],val[1]
            val = [val[i] for i in range(2,len(val))]
            if len(val) == 1:
                #flatten length 1 lists
                val = val[0]
            try:
                param.setRange(r_min,r_max)
                param.setValue(val)
            except AttributeError:
                #a list of parameters
                for p in param:
                    p.setRange(r_min,r_max)
                    p.setValue(val)
    
    def set_labrad_parameter(self, path, units):
        @inlineCallbacks
        def func(new_val):
            try:
                if type(new_val) == bool:
                    yield self.cxn.servers['Semaphore'].set_parameter(path, new_val, context = self.context)
                elif type(new_val) == list:
                    cur = yield self.cxn.servers['Semaphore'].get_parameter(path, context = self.context)
                    update = []
                    update.extend(cur[0:2])
                    new_val  = [self.WithUnit(el, units) for el in new_val]
                    update.extend(new_val)
                    yield self.cxn.servers['Semaphore'].set_parameter(path, update, context = self.context)
                else:
                    try:
                        new_val = self.WithUnit(new_val, units)
                    except TypeError:
                        if isinstance(new_val, QtCore.QString):
                            new_val = str(new_val)
                    minim,maxim,cur = yield self.cxn.servers['Semaphore'].get_parameter(path, context = self.context)
                    yield self.cxn.servers['Semaphore'].set_parameter(path, [minim,maxim,new_val], context = self.context)
            except Exception,e:
                raise e
        return( func)        
    