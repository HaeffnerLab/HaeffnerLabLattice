import sys

class importer(object):
    
    def __init__(self):
        self.init_modules = [x for x in sys.modules.keys()]

    def clear_modules(self):
        excess = [x for x in sys.modules.keys() if x not in self.init_modules]
        for m in excess:
            print m
            del(sys.modules[m]) 
    
    def print_constant(self):
        from constant import container
        print container.constant
        
if __name__ == '__main__':
    import time
    inst = importer()
    inst.print_constant()
    time.sleep(0.1)
    inst.clear_modules()
    inst.print_constant()