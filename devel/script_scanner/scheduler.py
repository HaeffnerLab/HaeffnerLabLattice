from twisted.internet.threads import deferToThread
from configuration import config 

class scheduler(object):
    
    def __init__(self):
        self.running = []
        self.queue = {}
        self.scheduled = {}
        self.scheduled_ID_counter = 0
        self.queue_ID_counter = 0

    def are_scans_running(self):
        return bool(self.running)
    
    def add_scan_to_queue(self, scan):
        scan_id= self.queue_ID_counter
        self.queue[scan_id] = scan
        self.queue_ID_counter += 1
        self.launch_scripts()
        return scan_id
    
    def remove_scan_from_queue(self, queue_ID):
        del self.queue[queue_ID]
    
    def remove_from_running(self, deferred_result, running_id):
        self.running.remove(running_id)
     
    def new_scheduled_scan(self, scan, period):
        '''
        @var period: in seconds
        '''
        lc = LoopingCall(self.add_script_to_queue, script)
        self.scheduled_scripts[self.scheduled_scripts_ID_counter] = lc
        self.scheduled_scripts_ID_counter += 1
        lc.start(period, now = True)
        #signal on new scheduled script
    
    def change_period_scheduled_script(self, scheduled_ID, period):
        try:
            lc = self.scheduled_scripts[scheduled_ID]
        except KeyError:
            raise Exception ("Schedule Script with {} ID does not exist".formatI(scheduled_ID))
        else:
            lc.stop()
            lc.start(period)        
    
    def cancel_scheduled_script(self, scheduled_ID):
        try:
            lc = self.scheduled_scripts[scheduled_ID]
        except KeyError:
            raise Exception ("Schedule Script with {} ID does not exist".formatI(scheduled_ID))
        else:
            lc.stop()
            del self.scheduled_scripts[scheduled_ID]

    def launch_scripts(self, result = None):
        if not self.queue:
            return
        non_conflicting = set()
        #find all non-conflicting experiments
        for running in self.running:
            non_conf = config.allowed_concurrent.get(running, [])
            non_conflicting = non_conflicting.union( (set(non_conf) ) )
        #launch the scan if no conflicts or if no scans are running
        earliest_id,scan = sorted(self.queue.iteritems())[0]
        if scan.script in non_conflicting or not self.are_scans_running():
            del self.queue[earliest_id]
            self.running.append(earliest_id)
            d = deferToThread(scan.execute)
            d.addCallback(self.remove_from_running, running_id = earliest_id) 
            d.addCallback(self.launch_scripts)
            self.launch_scripts()