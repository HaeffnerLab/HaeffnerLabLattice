from labrad.server import LabradServer, Signal

class Signals(LabradServer):
    
    on_running_new_script = Signal(200000 , "on_running_new_script", '(ws)')
    on_running_new_status = Signal(200001 , "on_running_new_status", '(wsv)')
    on_running_scipt_paused = Signal(200002 , "on_running_scipt_paused", 'wb')
    on_running_script_stopped = Signal(200003 , "on_running_script_stopped", 'w')
    on_running_sciprt_restarted = Signal(200004 , "on_running_sciprt_restarted", 'ww')#signal with a pair if IDs (id of script to restart, new issue id)
    on_running_sciprt_finished = Signal(200005 , "on_running_sciprt_finished", 'w')
    on_running_sciprt_finished_error = Signal(200006 , "on_running_sciprt_finished_error", 'ws')
    '''
    queued scripts
    '''
    on_queued_new_script = Signal(200010 , "on_queued_new_script", 'ws')
    on_queued_removed = Signal(200011 , "on_queued_removed", 'w')
    '''
    scheduled script signals
    '''
    on_scheduled_new_script = Signal(200020 , "on_scheduled_new_script", '(wsv)')
    on_scheduled_new_duration = Signal(200021 , "on_scheduled_new_duration", 'wv')
    on_scheduled_removed = Signal(200022 , "on_scheduled_removed", 'w')