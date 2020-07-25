from heapq import heappush, heappop, heapify

class MaxHeap():
    def __init__(self):
        self.heap = []

    def __getitem__(self, i):
        priority, value = self.heap[i]
        return (-1 * priority, value)

    def __setitem__(self, i, item):
        priority, value = item[0], item[1]
        self.heap[i] = (-1 * priority, value)

    def __len__(self):
        return len(self.heap)

    def push(self, priority, value):
        heappush(self.heap, (-1 * priority, value))
    
    def pop(self):
        priority, value = heappop(self.heap)
        return (-1 * priority, value)

    def heapify(self):
        heapify(self.heap)