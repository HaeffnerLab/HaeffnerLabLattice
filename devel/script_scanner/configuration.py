class config(object):

    #list in the format (import_path, class_name)
    scripts = [('sample_experiment', 'sample_experiment'),('sample_experiment', 'another_sample')]

    #experiments are allowed to run together
    allowed_concurrent = {
        ('sample_experiment', 'sample_experiment'): None,
        ('sample_experiment', 'another_sample'): None,
    }
    
    launch_history = 1000               
