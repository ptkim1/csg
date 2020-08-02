from heapq import heappush, heappop, heapify

class MaxHeap():
    """
    A class that implements a priority max heap using python's built-in heapq (which converts lists to min-heaps)

    No public attributes

    Methods
    -------
    push(priority, item)
        Pushes item to heap with given priority
    
    pop()
        Pops and returns item from heap with highest priority

    heapify()
        Call to restore heap state after changes made by __setitem__
    """
    
    def __init__(self):
        self._heap = []

    def __getitem__(self, i):
        priority, value = self._heap[i]
        return (-1 * priority, value)

    def __setitem__(self, i, item):
        priority, value = item[0], item[1]
        self._heap[i] = (-1 * priority, value)

    def __len__(self):
        return len(self._heap)

    def push(self, priority: float, item):
        """
        Pushes item to heap w/ given priority
        """
        heappush(self._heap, (-1 * priority, item))
    
    def pop(self):
        """
        Removes and returns highest-priority item from the heap
        """
        priority, value = heappop(self._heap)
        return (-1 * priority, value)

    def heapify(self):
        """
        Restores heap state, to be called by user after setter methods have 
        changed priorities in the heap
        """
        heapify(self._heap)