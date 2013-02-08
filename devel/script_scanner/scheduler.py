from twisted.internet.threads import deferToThread
from twisted.internet.defer import Deferred
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
        self.queue = {} #dictionary in the form identification : scan to launch
        self.launch_history = []
        self.scheduled = {}
        self.scheduled_ID_counter = 0
        self.scan_ID_counter = 0
        
    def are_scans_running(self):
        return bool(self.running)
    
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
        for ident, scan in sorted(self.queue.iteritems()):
            queue.append((ident, scan.name))
        return queue
    
    def remove_queued_script(self, script_ID):
        if script_ID in self.queue.keys():
            del self.queue[script_ID]
            self.signals.on_queued_removed(script_ID)
        else:
            raise Exception("Tring to remove scirpt ID {0} from queue but it's not in the queue")
    
    def restart_script(self, ident):
        d = dict(self.launch_history)
        scan = d.get(ident, None)
        if scan is None:
            raise Exception ("Can not restart script that is not in the launch history")
        else:
            scan_id = self.add_scan_to_queue(scan)
            self.signals.on_running_script_restarted((ident, scan_id))
            return scan_id
        
    def add_scan_to_queue(self, scan):
        scan_id= self.scan_ID_counter
        self.queue[scan_id] = scan
        self.scan_ID_counter += 1
        self.signals.on_queued_new_script((scan_id, scan.name))
        self.launch_scripts()
        return scan_id
    
    def add_external_scan(self, scan):
        scan_id= self.scan_ID_counter
        self.scan_ID_counter += 1
        status = script_semaphore(scan_id, self.signals)
        self.running[scan_id] = running_script(scan, Deferred(), status , externally_launched = True)
        return scan_id
        
    def remove_from_running(self, deferred_result, running_id):
        del self.running[running_id]
    
    def remove_if_external(self, running_id):
        if running_id in self.get_running_external():
            self.remove_from_running(None, running_id)
     
    def new_scheduled_scan(self, scan, period):
        '''
        @var period: in seconds
        '''
        lc = LoopingCall(self.add_scan_to_queue, scan)
        new_schedule_id = self.scheduled_ID_counter
        self.scheduled[new_schedule_id] = (scan.name, lc)
        self.scheduled_ID_counter += 1
        lc.start(period, now = True)
        self.signals.on_scheduled_new_script((new_schedule_id, scan.name, period))
        return new_schedule_id
    
    def change_period_scheduled_script(self, scheduled_ID, period):
        try:
            name,lc = self.scheduled[scheduled_ID]
        except KeyError:
            raise Exception ("Schedule Script {0} with {1} ID does not exist".format(name, scheduled_ID))
        else:
            lc.stop()
            lc.start(period)
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
        if not self.queue:
            return
        non_conflicting = set()
        #find all non-conflicting experiments
        for running in self.running.keys():
            non_conf = config.allowed_concurrent.get(running, [])
            non_conflicting = non_conflicting.union( (set(non_conf) ) )
        #launch the scan if no conflicts or if no scans are running
        earliest_id,scan = sorted(self.queue.iteritems())[0]
        if scan.script_cls.name() in non_conflicting or not self.are_scans_running():
            #launching the script:
            #firt add to history of launches
            self.launch_history.append((earliest_id, scan))
            if len(self.launch_history) > config.launch_history:
                self.launch_history.pop(0)
            #remove from queue
            del self.queue[earliest_id]
            self.signals.on_queued_removed(earliest_id)
            #make a deferred, and starts things moving
            d = Deferred()
            status = script_semaphore(earliest_id, self.signals)
            self.running[earliest_id] = running_script(scan, d, status)
            d.addCallback(self.launch_in_thread, scan, earliest_id)
            d.addCallback(self.remove_from_running, running_id = earliest_id) 
            d.addCallback(self.launch_scripts)
            d.callback(True)
            self.signals.on_running_new_script((earliest_id, scan.name))
            #see of any other script can be launched
            self.launch_scripts()
    
    def launch_in_thread(self, result, scan, ident):
        d = deferToThread(scan.execute, ident)
        return d