class config(object):

    #list in the format (import_path, class_name)
    scripts = [('sample_experiment', 'sample_experiment')]

    #experiments are allowed to run together
    allowed_concurrent = {
        ('sample_experiment', 'sample_experiment'): None
    }
    
    launch_history = 1000               
