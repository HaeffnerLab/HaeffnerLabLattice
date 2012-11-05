from twisted.internet.defer import inlineCallbacks

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
        from labrad import types as T
        self.T = T
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
                #if a list
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
            try:
                param.setRange(val[0],val[1])
                param.setValue(val[2])
            except AttributeError:
                #a list
                for p in param:
                    p.setRange(val[0],val[1])
                    p.setValue(val[2])
    
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
                    new_val  = [self.T.Value(el, units) for el in new_val]
                    update.extend(new_val)
                    yield self.cxn.servers['Semaphore'].set_parameter(path, update, context = self.context)
                else:
                    new_val = self.T.Value(new_val, units)
                    minim,maxim,cur = yield self.cxn.servers['Semaphore'].get_parameter(path, context = self.context)
                    yield self.cxn.servers['Semaphore'].set_parameter(path, [minim,maxim,new_val], context = self.context)
            except Exception,e:
                print e
        return( func)        
    