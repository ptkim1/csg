import numpy as np
import json
import pickle


# whats the order to put regular vs class versus getter methods

class BaseSeating:
    """
    A class that represents a seating arrangement for an event/plane/bus etc.

    Attributes
    ----------
    totalseats: int
        total number of seats (filled and empty)
    seating: np.ndarray
        numpy array used to represent the state of the seating. 
        -1 indicates no seat at these coordinates (an aisle for example)
        0 indicates an empty seat
        Any other number indicates a person from that group is sitting here
    unfilledseats: int
        number of remaining empty seats
    emptyseatcoords: set[tuple(x, y)]
        a set of tuples where each tuple represents a coordinate in seating that 
        is currently an empty seat

    Methods
    -------
    isemptyseat(x, y)
        checks if (x, y) is a coordinate where there is an empty seat
    
    areemptyseats(coordlist)
        checks if the list of tuples in coordlist are empty seats
        returns True only if all seats in coordlist are empty

    add_person(x, y, groupid)
        adds a person to seat (x, y) with group id groupid
        raises a warning but does nothing if the seat is not empty

    add_many(coordlist, groupid)
        adds multiple people from the same group to the seats specified
        in coordlist
    
    to_pickle(name)
        saves seating in a pickle
    
    from_pickle(name)
        loads an seating object from pickle

    from_json(name)
        loads a seating arrangement based on parameters in a json file 

    from_regular_blocks(block_dims, tiling)
        returns a seating that is made up of uniform blocks of seats spaced by 
        aisles at regular intervals
    """

    def __init__(self, totalseats: int, seating: np.ndarray):
        """
        Creates a BaseSeating object

        totalseats: int
            the number of total available seats
        seating: np.ndarray
            array holding the representation of the seating, with 0 for empty seats and -1
            for locations that do not contain a seat
        """
        # to docstring: add that -1 means no seat, 0 means empty seat, any other number means filled seat
        self.totalseats = totalseats
        self.seating = seating
        self.unfilledseats = totalseats
        self.emptyseatcoords = set((x, y) for x, y in zip(np.where(self.seating == 0)[0],
                                                       np.where(self.seating == 0)[1]
                                                       )
                                )

    def isemptyseat(self, x, y):
        """
        checks if (x, y) is a coordinate where there is an empty seat
        """
        if (x, y) in self.emptyseatcoords:
            return True
        else:
            return False

    def areemptyseats(self, coordlist):
        """
        checks if coords in coordlist are empty seats
        coordlist must be a list of tuples (x, y)
        returns true if all seats in the coordlist are empty, false otherwise
        """
        for coord in coordlist:
            if not self.isemptyseat(coord[0], coord[1]):
                return False
        return True

    def add_person(self, x, y, groupid):
        """
        Tries to add a person from group groupid to the seat at (x, y)
        Raises a warning and does nothing if seat is emptys
        """
        if not self.isemptyseat(x, y):
            raise Warning('Trying to place person at invalid location ({}, {})'.format(x, y))
        else:
            self.seating[x, y] = groupid # set the seat to be filled by this group
            self.unfilledseats -= 1 # one less unfilled seat
            self.emptyseatcoords.remove((x, y)) # remove the newly filled seat from emptyseatcoords
            return True

    def add_many(self, coordlist, groupid):
        """
        adds a person from groupid to each tuple (x, y) in coordlist
        """
        for coord in coordlist:
            self.add_person(coord[0], coord[1], groupid)

    def to_pickle(self, name):
        """
        saves seating in a pickle at saved/objs/[name]
        """
        pickle.dump(open('saved/objs/{}'.format(name), 'wb'))

    @classmethod
    def from_pickle(cls, name):
        """
        loads an seating object from pickle at saved/objs/[name]
        """
        return pickle.load(open('saved/objs/{}'.format(name), 'rb'))

    @classmethod
    def from_json(cls, name):
        """
        loads a seating arrangement based on parameters in a json file at
        saved/settings/[name]
        """
        inputs = json.load(open('saved/settings/{}'.format(name))) # read json

        seating = np.zeros(inputs['dimensions']) # initialize seating with zeros
        for row in inputs['emptyrows']:
            seating[:, row] = -1 # all coords at row are not seats
        for column in inputs['emptycols']:
            seating[column, :] = -1 # all coords at column are not seats
        for box in inputs['emptyboxes']:
            # all coords within the box bound by box[0]: box[1] and box[2] : box[3] are not seats
            seating[box[0] : box[1], box[2] : box[3]] = -1
        
        for singlegap in inputs['gaps']: 
            # all coords in gaps are non-seat locations
            seating[singlegap[0], singlegap[1]] = -1

        totalseats = inputs['dimensions'][0] * inputs['dimensions'][1] + np.sum(seating)
        # add here bc non-seats are -1. 

        return cls(totalseats, seating)

    @classmethod
    def from_regular_blocks(cls, block_dims, tiling):
        """
        returns a seating that is made up of uniform blocks of seats spaced by 
        aisles at regular intervals
        
        block_dims: a two element list or tuple that specifies the dimensions of each
                    regular block
        tiling: a two element list or tuple that specifies the tiling of each block in
                    the x and y dimension
        """
        # total number of rows and cols
        xdim = (block_dims[0] * tiling[0]) + (tiling[0] - 1)
        ydim = (block_dims[1] * tiling[1]) + (tiling[1] - 1)

        # figure out where the aisles are in x and y axes
        xaisles = list(range(block_dims[0], xdim-block_dims, block_dims[0]+1))
        yaisles = list(range(block_dims[1], ydim-block_dims, block_dims[1]+1))

        # compute total number of seats
        total_seats = (block_dims[0] * block_dims[1]) * (tiling[0] * tiling[1])

        # make seating
        seating = np.zeros((xdim, ydim))
        seating[xaisles, :] = -1
        seating[:, yaisles] = -1

        return cls(total_seats, seating)
    
class LengthWidthSeating(BaseSeating):
    """
    A class that represents a seating arrangement for an event/bus/plane etc, 
    where the dimensions of the rows and columns are not unit, but variable. 

    Attributes
    ----------
    totalseats: int
        total number of seats (filled and empty)
    seating: np.ndarray
        numpy array used to represent the state of the seating. 
        -1 indicates no seat at these coordinates (an aisle for example)
        0 indicates an empty seat
        Any other number indicates a person from that group is sitting here
    unfilledseats: int
        number of remaining empty seats
    emptyseatcoords: set[tuple(x, y)]
        a set of tuples where each tuple represents a coordinate in seating that 
        is currently an empty seat
    seatlen: float
        length (y dimension) of each row
    seatwidth: float
        width (x dimension) of each column
    """
    def __init__(self, totalseats: int, seating: np.ndarray, seatlen, seatwidth):
        """
        Creates a LengthWidthSeating object

        totalseats: int
            the number of total available seats
        seating: np.ndarray
            array holding the representation of the seating, with 0 for empty seats and -1
            for locations that do not contain a seat
        seatlen: float
            length (y dimension) of each row
        seatwidth: float
            width (x dimension) of each column
        """
        super().__init__(totalseats, seating)
        self.seatlen = seatlen
        self.seatwidth = seatwidth

    @classmethod
    def from_json(cls, name):
        """
        Creates a LengthWidthSeating based on parameters in a json file
        at saved/settings/[name]. Json must include field for 
        seatlen and seatwidth
        """
        seating = BaseSeating.from_json(name)
        inputs = json.load(open('saved/settings/{}'.format(name)))
        
        seating.seatlen = inputs['seatlen']
        seating.seatwidth = inputs['seatwidth']

        return seating
    
