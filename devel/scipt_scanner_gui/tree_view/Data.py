class Node(object):
    
    def __init__(self, name, parent=None): 
        super(Node, self).__init__()
        self._name = name
        self._children = []
        self._parent = parent
        if parent is not None:
            parent.addChild(self)

    def addChild(self, child):
        self._children.append(child)
        child._parent = self

    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False
        
        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):
        if position < 0 or position > len(self._children):
            return False
        child = self._children.pop(position)
        child._parent = None
        return True

    def name(self):
        return self._name
    
    def filter_text(self):
        return self.name()

    def child(self, row):
        return self._children[row]
    
    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent
    
    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def data(self, column):
        if column is 0: return self.name()
    
    def setData(self, column, value):
        pass

class CollectionNode(Node):
    def __init__(self, name, parent = None):
        super(CollectionNode, self).__init__(name, parent)
    
class ParameterNode(Node):
    
    def __init__(self, name, parent=None):
        super(ParameterNode, self).__init__(name, parent)
        self._collection = parent.name()
        self._min = 0
        self._max = 100
        self._value = 0
        self._units = 'MHz'

    def data(self, column):
        if column < 1:
            return super(ParameterNode, self).data(column)
        elif column == 1:
            return self.__repr__()
        elif column == 2:
            return self._collection
        elif column == 3:
            return self._min
        elif column == 4:
            return self._max
        elif column == 5:
            return self._value
        elif column == 6:
            return self._units
    
    def filter_text(self):
        return self.parent().name() + self.name()
    
    def __repr__(self):
        return '{0} {1}'.format(self._value, self._units)
        
    def setData(self, column, value):
        value = value.toPyObject()
        if column == 3:
            self._min = value
        elif column == 4:
            self._max = value
        elif column == 5:
            self._value = value
        elif column == 6:
            self._units = value

class ScanNode(Node):
    def __init__(self, name, parent=None):
        super(ScanNode, self).__init__(name, parent)

        self._min = 0
        self._max = 100
        self._scan_start = 1.0
        self._scan_stop = 50.0
        self._scan_points = 10
        self._units = 'MHz'
    
    def filter_text(self):
        return self.parent().name() + self.name()
    
    def data(self, column):
        if column < 1:
            return super(ScanNode, self).data(column)
        elif column == 1:
            return self.__repr__()
    
    def __repr__(self):
        return 'Scan {0} {3} to {1} {3} in {2} steps'.format(self._scan_start, self._scan_stop, self._scan_points, self._units)
        
    def setData(self, column, value):
        pass