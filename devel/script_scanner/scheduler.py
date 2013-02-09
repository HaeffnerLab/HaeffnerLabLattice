from twisted.internet.threads import deferToThread
from twisted.internet.defer import Deferred, DeferredList
from configuration import config 
from twisted.internet.task import LoopingCall
from script_status import script_semaphore

class running_script(object):
    '''holds information about a script that is currently running'''
    def __init__(self, scan, defer_on_done, status, externally_launched = False):
        self.scan = scan
        self.name = scan.name
        self.status = status
        self.defer_on_done = defer_on_done
        self.externally_launched = externally_launched

class scheduler(object):
    
    def __init__(self, signals):
        self.signals = signals
        self.running = {} #dictionary in the form identification : running_script_instance
        self.queue = [] #list where each element is in the form (ident, experiment)
        self.urgent_task_running = False
        self.launch_history = []
        self.scheduled = {}
        self.unpause_on_finish = {} #dictionary in the form experiment ident : set identifications to unpause when done
        self.scheduled_ID_counter = 0
        self.scan_ID_counter = 0
    
    def running_deferred_list(self):
        return [script.defer_on_done for script in self.running.itervalues() if not script.externally_launched]
    
    def get_running_external(self):
        return [ident for (ident, script) in self.running.iteritems() if script.externally_launched]
        
    def get_running(self):
        running = []
        for ident, script in self.running.iteritems():
            running.append((ident, script.name))
        return running
    
    def get_running_status(self, ident):
        script = self.running.get(ident, None)
        if script is None:
            return None
        else:
            return script.status
    
    def get_scheduled(self):
        scheduled = []
        for ident, (scan_name, loop) in self.scheduled.iteritems():
            scheduled.append([ident, scan_name, loop.interval])
        return scheduled
    
    def get_queue(self):
        queue = []
        for ident, scan, urgent in self.queue:
            queue.append((ident, scan.name))
        return queue
    
    def remove_queued_script(self, script_ID):
        removed = False
        for ident, scan, urgent in self.queue:
            if script_ID == ident: 
                removed = True
                self.queue.remove((script_ID, scan, urgent))
                self.signals.on_queued_removed(script_ID)
        if not removed:
            raise Exception("Tring to remove scirpt ID {0} from queue but it's not in the queue".format(script_ID))
            
    def add_scan_to_queue(self, scan, priority = 'Normal'):
        #increment counter
        scan_id = self.scan_ID_counter
        self.scan_ID_counter += 1
        #add to queue
        if priority == 'Normal':
            self.queue.append((scan_id, scan, False))
            self.signals.on_queued_new_script((scan_id, scan.name, True))
            self.launch_scripts()
        elif priority == 'First in Queue':
            self.queue.insert(0, (scan_id, scan, False))
            self.signals.on_queued_new_script((scan_id, scan.name, False))
            self.launch_scripts()
        elif priority == 'Pause All Others':
            if not self.urgent_task_running:
                self.launch_urgent_pausing_normal(scan_id, scan)
            else:
                #if other urgent tasks are running, put current one in the queue
                self.queue.insert(0, (scan_id, scan, True))
                self.signals.on_queued_new_script((scan_id, scan.name, False))
        else: 
            raise Exception ("Unrecognized priority type")
        return scan_id
    
    def launch_urgent_pausing_normal(self, scan_id, scan):
        '''
        first pauses all scripts that are currently running and conflict with with the scan
        then launches the scan. At the end the pause scripts are unpaused
        '''
        self.urgent_task_running = True
        paused_idents, d  = self.pause_conflicting(scan.name)
        d.addCallback(self.insert_first_callback, (scan_id, scan))
        paused_idents = set(paused_idents)
        self.unpause_on_finish[scan_id] = paused_idents
        
    def insert_first_callback(self, result, to_insert):
        scan_id, scan = to_insert
        self.add_to_history(scan_id, scan)
        self.do_launch(scan_id, scan)
        
    def pause_conflicting(self, name):
        paused_identification = []
        paused = []
        for ident, script in self.running.iteritems():
            non_conf = config.allowed_concurrent.get(script.name, [])
            if not name in non_conf:
                paused_identification.append(ident)
                d = script.status.set_pausing(True)
                paused.append(d)
        paused_deferred = DeferredList(paused)
        return paused_identification, paused_deferred
        
    def get_non_conflicting(self):
        '''
        returns a list of experiments that can run concurrently with current experiments
        '''
        non_conflicting = []
        for running, script in self.running.iteritems():
            cls_name = script.scan.script_cls.name()
            non_conf = config.allowed_concurrent.get(cls_name, None)
            if non_conf is not None:
                non_conflicting.append(set(non_conf))
        if non_conflicting:
            return set.intersection(*non_conflicting)
        else:
            return set()
       
        return non_conflicting
    
    def add_external_scan(self, scan):
        scan_id= self.scan_ID_counter
        self.scan_ID_counter += 1
        status = script_semaphore(scan_id, self.signals)
        self.running[scan_id] = running_script(scan, Deferred(), status , externally_launched = True)
        return scan_id
        
    def remove_from_running(self, deferred_result, running_id):
        del self.running[running_id]
        self.finish_urgent(running_id)
    
    def finish_urgent(self, running_id):
        #check the queue: if there's another urgent task launch that one. otherwise, unpause the previously paused tasks
        if running_id in self.unpause_on_finish.keys():
            to_unpause = self.unpause_on_finish[running_id]
            del self.unpause_on_finish[running_id]
        else:
            to_unpause = set()
        if to_unpause:
            self.do_unpause_on_finish(to_unpause)

    def do_unpause_on_finish(self, to_unpause):
        to_unpause_deferred = []
        for ident in to_unpause:
            try:
                d = self.running[ident].status.set_pausing(False)
                to_unpause_deferred.append(d)
            except KeyError:
                print 'tried to unpause ID {0} but no longer running'.format(ident)
        to_unpause_deferred = DeferredList(to_unpause_deferred)
        to_unpause_deferred.addCallback(self.check_launch_another_urgent)
                
    def check_launch_another_urgent(self, result):
        try:
            ident, scan, urgent = self.queue[0]
            if urgent:
                self.launch_urgent_pausing_normal(ident, scan)
        except IndexError:
            self.urgent_task_running = False
            
    def remove_if_external(self, running_id):
        if running_id in self.get_running_external():
            self.remove_from_running(None, running_id)
     
    def new_scheduled_scan(self, scan, period, priority, start_now):
        '''
        @var period: in seconds
        '''
        lc = LoopingCall(self.add_scan_to_queue, scan, priority)
        new_schedule_id = self.scheduled_ID_counter
        self.scheduled[new_schedule_id] = (scan.name, lc)
        self.scheduled_ID_counter += 1
        lc.start(period, now = start_now)
        self.signals.on_scheduled_new_script((new_schedule_id, scan.name, period))
        return new_schedule_id
    
    def change_period_scheduled_script(self, scheduled_ID, period):
        try:
            name,lc = self.scheduled[scheduled_ID]
        except KeyError:
            raise Exception ("Schedule Script {0} with {1} ID does not exist".format(name, scheduled_ID))
        else:
            lc.stop()
            lc.start(period, now = False)
            self.signals.on_scheduled_new_duration((scheduled_ID, period))
    
    def cancel_scheduled_script(self, scheduled_ID):
        try:
            name, lc = self.scheduled[scheduled_ID]
        except KeyError:
            raise Exception ("Scheduled Script with ID {0} does not exist".format(scheduled_ID))
        else:
            lc.stop()
            del self.scheduled[scheduled_ID]
            self.signals.on_scheduled_removed(scheduled_ID)

    def launch_scripts(self, result = None):
        try:
            ident, scan, urgent = self.queue[0]
        except IndexError:
            return
        else:
            non_conflicting = self.get_non_conflicting()
            if scan.script_cls.name() in non_conflicting or not self.running:
                #firt add to history of launches
                self.add_to_history(ident, scan)
                #remove from queue and launch
                self.queue.pop(0)
                self.signals.on_queued_removed(ident)
                self.do_launch(ident, scan)
                self.launch_scripts()
                
    def add_to_history(self, ident, scan):
        self.launch_history.append((ident, scan))
        if len(self.launch_history) > config.launch_history:
            self.launch_history.pop(0)
    
    def do_launch(self, ident, scan ):
        d = Deferred()
        status = script_semaphore(ident, self.signals)
        self.running[ident] = running_script(scan, d, status)
        d.addCallback(self.launch_in_thread, scan, ident)
        d.addCallback(self.remove_from_running, running_id = ident) 
        d.addCallback(self.launch_scripts)
        d.callback(True)
        self.signals.on_running_new_script((ident, scan.name))
    
    def launch_in_thread(self, result, scan, ident):
        d = deferToThread(scan.execute, ident)
        return d