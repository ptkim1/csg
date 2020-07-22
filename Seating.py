import numpy as np
import json
import pickle


# whats the order to put regular vs class versus getter methods

class BaseSeating:
    def __init__(self, totalseats: int, seating: np.ndarray):
        # to docstring: add that -1 means no seat, 0 means empty seat, any other number means filled seat
        self.totalseats = totalseats
        self.seating = seating
        self.unfilledseats = totalseats
        self.max_x, self.max_y = seating.shape
        self.emptyseatcoords = set((x, y) for x, y in zip(np.where(self.seating == 0)[0],
                                                       np.where(self.seating == 0)[1]
                                                       )
                                )

    def nseats(self):
        return self.totalseats

    def unfilled(self):
        return self.unfilledseats

    def getseating(self):
        return self.seating

    def isemptyseat(self, x, y):
        if (x, y) in self.emptyseatcoords:
            return True
        else:
            return False

    def areemptyseats(self, coordlist):
        # if coordlist is empty return an error
        for coord in coordlist:
            if not self.isemptyseat(coord[0], coord[1]):
                return False
        return True

    def add_person(self, x, y, groupid):
        if not self.isemptyseat(x, y):
            # raise an error
            return False
        else:
            self.seating[x, y] = groupid
            self.unfilledseats -= 1
            self.emptyseatcoords.remove((x, y))
            return True

    def add_many(self, coordlist, groupid):
        for coord in coordlist:
            self.add_person(coord[0], coord[1], groupid)


    def move_person(self, init_x, init_y, new_x, new_y):
        if self.seating[init_x, init_y] > 0 and self.seating[new_x, new_y] == 0:
            self.seating[new_x, new_y] = self.seating[init_x, init_y]
            self.seating[init_x, init_y] = 0
            return True
        else:
            print('init seat empty or new seat full/invalid')
            return False

    def to_pickle(self, name):
        pickle.dump(open('saved/objs/{}'.format(name), 'wb'))

    @classmethod
    def from_pickle(cls, name):
        return pickle.load(open('saved/objs/{}'.format(name), 'rb'))

    @classmethod
    def from_json(cls, name):
        inputs = json.load(open('saved/settings/{}'.format(name)))
        # if not self._validate(inputs):
        #     # raise error
        #     print('error')

        seating = np.zeros(inputs['dimensions'])
        for row in inputs['emptyrows']:
            seating[:, row] = -1
        for column in inputs['emptycols']:
            seating[column, :] = -1
        for box in inputs['emptyboxes']:
            seating[box[0] : box[1], box[2] : box[3]] = -1
            # I need to validate this to make sure it works
        for singlegap in inputs['gaps']:
            seating[singlegap[0], singlegap[1]] = -1

        totalseats = inputs['dimensions'][0] * inputs['dimensions'][1] + np.sum(seating)
        # add here bc non-seats are -1. 

        return cls(totalseats, seating)

    @classmethod
    def from_regular_blocks(cls, block_dims, tiling):
        xdim = (block_dims[0] * tiling[0]) + (tiling[0] - 1)
        ydim = (block_dims[1] * tiling[1]) + (tiling[1] - 1)

        xaisles = list(range(block_dims[0], xdim-block_dims, block_dims[0]+1))
        yaisles = list(range(block_dims[1], ydim-block_dims, block_dims[1]+1))

        total_seats = (block_dims[0] * block_dims[1]) * (tiling[0] * tiling[1])
        seating = np.zeros((xdim, ydim))
        seating[xaisles, :] = -1
        seating[:, yaisles] = -1

        return cls(total_seats, seating)

    

    def _validate(self, parameters):
        if parameters['max_x'] <= 0 or parameters['max_y'] <= 0:
            return False
    


# class SeatingFromTicketMaster

    
