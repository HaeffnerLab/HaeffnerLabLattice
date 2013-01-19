class config(object):

    #dictionary in the form name: (import_path, class_name)
    scripts = {
     'First Test':  ('test_experiment', 'test1'),
     }
    
    #what experiments are allowed to run together
    allowed_concurrent = {
        'First Test': None                  
    }