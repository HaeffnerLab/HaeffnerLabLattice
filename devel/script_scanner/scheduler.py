from twisted.internet.threads import deferToThread
from twisted.internet.defer import Deferred
from configuration import config 
from twisted.internet.task import LoopingCall
from script_status import script_semaphore 

class running_script(object):
    '''holds information about a script that is currently running'''
    def __init__(self, scan, defer_on_done, externally_launched = False):
        self.scan = scan
        self.name = scan.name
        self.status = script_semaphore()
        self.defer_on_done = defer_on_done
        self.externally_launched = externally_launched

class scheduler(object):
    
    def __init__(self, signal_on_new_status):
        self.running = {} #dictionary in the form identification : running_script_instance
        self.queue = {} #dictionary in the form identification : scan to launch
        self.launch_history = []
        self.scheduled = {}
        self.scheduled_ID_counter = 0
        self.scan_ID_counter = 0
        self.signal_on_new_status = signal_on_new_status
        self.signal_on_new_status(1, 'hi', 50.0)
    
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
            queue.append((ident, scan.scan_name))
        return queue
    
    def clear_queue(self):
        for item in self.queue.keys():
            self.remove_scan_from_queue(item)
    
    def restart_script(self, ident):
        d = dict(self.launch_history)
        scan = d.get(ident, None)
        if scan is None:
            raise Exception ("Can not restart script that is not in the launch history")
        else:
            scan_id = self.add_scan_to_queue(scan)
            return scan_id
        
    def add_scan_to_queue(self, scan):
        scan_id= self.scan_ID_counter
        self.queue[scan_id] = scan
        self.scan_ID_counter += 1
        self.launch_scripts()
        return scan_id
    
    def add_external_scan(self, scan):
        scan_id= self.scan_ID_counter
        self.scan_ID_counter += 1
        d = Deferred()
        d.addCallback(self.remove_from_running, scan_id)
        self.running[scan_id] = running_script(scan, d, externally_launched = True)
        return scan_id
        
    def remove_scan_from_queue(self, queue_ID):
        del self.queue[queue_ID]
        #need signal
    
    def remove_from_running(self, deferred_result, running_id):
        del self.running[running_id]
        #need signal
     
    def new_scheduled_scan(self, scan, period):
        '''
        @var period: in seconds
        '''
        lc = LoopingCall(self.add_scan_to_queue, scan)
        new_schedule_id = self.scheduled_ID_counter
        self.scheduled[new_schedule_id] = (scan.scan_name, lc)
        self.scheduled_ID_counter += 1
        lc.start(period, now = True)
        return new_schedule_id
        #signal on new scheduled script
    
    def change_period_scheduled_script(self, scheduled_ID, period):
        try:
            name,lc = self.scheduled[scheduled_ID]
        except KeyError:
            raise Exception ("Schedule Script {0} with {1} ID does not exist".format(name, scheduled_ID))
        else:
            lc.stop()
            lc.start(period)
        #signal
    
    def cancel_scheduled_script(self, scheduled_ID):
        try:
            name, lc = self.scheduled[scheduled_ID]
        except KeyError:
            raise Exception ("Schedule Script {0} with {1} ID does not exist".format(name, scheduled_ID))
        else:
            lc.stop()
            del self.scheduled[scheduled_ID]

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
        if scan.script in non_conflicting or not self.are_scans_running():
            #launching the script:
            #firt add to history of launches
            self.launch_history.append((earliest_id, scan))
            if len(self.launch_history) > config.launch_history:
                self.launch_history.pop(0)
            #remove from queue
            del self.queue[earliest_id]
            #make a deferred, and starts things moving
            d = Deferred()
            self.running[earliest_id] = running_script(scan, d)
            d.addCallback(self.launch_in_thread, scan, earliest_id)
            d.addCallback(self.remove_from_running, running_id = earliest_id) 
            d.addCallback(self.launch_scripts)
            d.callback(True)
            #see of any other script can be launched
            self.launch_scripts()
    
    def launch_in_thread(self, result, scan, ident):
        d = deferToThread(scan.execute, ident)
        return d