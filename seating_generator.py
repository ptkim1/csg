import numpy as np
import json
import pickle


class BaseSeating:
    def __init__(self, totalseats: int, seating: np.ndarray):
        # to docstring: add that -1 means no seat, 0 means empty seat, 1 means filled seat
        self.totalseats = totalseats
        self.seating = seating
        self.unfilledseats = totalseats
        self.max_x, self.max_y = seating.shape

    def nseats(self):
        return self.totalseats

    def unfilled(self):
        return self.unfilledseats

    def getseating(self):
        return self.seating

    def _valid(self, x, y):
        if x >= self.max_x or y >= self.max_y or x < 0 or y < 0:
            # raise an error - index out of bounds
            print('index out of bounds') 
            return False
        return True

    def add_person(self, x, y):
        if self.unfilledseats == self.totalseats:
            print('cannot add, seating is full')
        elif not self._valid(x, y):
            print('we need an error here, saying we are out of bounds')
        elif not self.seating[x, y]:
            self.seating[x, y] = 1
            self.unfilledseats -= 1
        elif self.seating[x, y] == -1:
            # raise an error - no seat here
            print('we need an error here later, saying theres no seat')
        elif self.seating[x, y] == 1:
            # raise an error - seat already filled
            print('seat already filled')
        else:
            print('this case should not be possible')

    def move_person(self, init_x, init_y, new_x, new_y):
        if not self._valid(init_x, init_y) or not self._valid(new_x, new_y):
            print('index out of bounds')
        elif self.seating[init_x, init_y] == 1 and self.seating[new_x, new_y] == 0:
            self.seating[init_x, init_y] = 0
            self.seating[new_x, new_y] = 1
        else:
            print('init seat empty or new seat full/invalid')

    def to_pickle(self, name):
        pickle.dump(open('seatings/{}'.format(name), 'wb'))

class SeatingFromJson(BaseSeating):
    def __init__(self, path):
        inputs = json.load(open('seating_settings/{}'.format(path)))
        if not self._validate(inputs):
            # raise error
            print('error')

        seating = np.zeros(inputs['dimensions'])
        for row in inputs['emptyrows']:
            seating[row, :] = -1
        for column in inputs['emptycols']:
            seating[:, column] = -1
        for box in inputs['emptyboxes']:
            seating[box[0] : box[1], box[2] : box[3]] = -1
            # I need to validate this to make sure it works
        for singlegap in inputs['gaps']:
            seating[singlegap] = -1

        totalseats = inputs['dimensions'][0] * inputs['dimensions'][1] + np.sum(seating)
        # add here bc non-seats are -1. 

        super().__init__(totalseats, seating)

    def _validate(self, parameters):
        if parameters['max_x'] <= 0 or parameters['max_y'] <= 0:
            return False
         


# class SeatingFromTicketMaster

    
