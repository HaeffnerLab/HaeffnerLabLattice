
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
        return scan_id
    
    def remove_scan_from_queue(self, queue_ID):
        del self.queue[queue_ID]
     
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

    def scripts_to_start(self):
        pass
        
#        to_start = []
#        conflicting = set() #set of conflicting experiments
#        for script in self.queue:
#            
#        
#        
#        return None