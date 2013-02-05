class config(object):

    #list in the format (import_path, class_name)
    scripts = [('test_experiment', 'test1')]

    #experiments are allowed to run together
    allowed_concurrent = {
        ('test_experiment', 'test1'): None
    }
    
    launch_history = 1000               
