from Seating import BaseSeating
from Attendees import BaseAttendees
from abc import abstractmethod
import numpy as np
import random
import copy
from scipy.spatial.distance import pdist, squareform
from utils import MaxHeap


class BaseSolver:
    """
    Abstract base class that represents a Solver object, which takes a
    BaseSeating and a BaseAttendees and places all the attendees into seats

    Attributes
    ----------
    seating: BaseSeating
        a BaseSeating object in which the attendees will be placed
    attendees: BaseAttendees
        a BaseAttendees object from which the attendees will be drawn

    Methods
    -------
    solve()
        Adds all the attendees to the seating, if possible

    In the current implementation, groups are restricted to sizes 1-4. 
    Groups of 2 and 3 must be seated side-to-side, while groups of four may be seated
    in two rows of 2, or one row of 4.

    """
    def __init__(self, seating: BaseSeating, attendees: BaseAttendees):
        """
        Creates a Solver with specified seating and attendees
        """
        self.seating = seating
        self.attendees = attendees

    @abstractmethod
    def solve(self):
        """
        Children must implement the solve() method
        """
        pass


    def _group_here_ok(self, group, x, y):
        """
        Checks if it is possible to place a group with size group at the given coordinates x, y. 
        """
        selection = {
            1: self._1_check,
            2: self._2_check,
            3: self._3_check,
            4: self._4_check
        }
        return selection[group](x, y)

    def _1_check(self, x, y):
        """
        Checks if this seat is empty
        """
        return self.seating.isemptyseat(x, y)
    
    def _2_check(self, x, y):
        """
        Checks if it is possible to put a group of two, with one of the two seated
        at the coordinates x, y
        """
        # seat and seat to the right are empty
        cond1 = (self.seating.isemptyseat(x, y) and self.seating.isemptyseat(x+1, y))

        # seat and seat to the left are empty
        cond2 = (self.seating.isemptyseat(x, y) and self.seating.isemptyseat(x-1, y))

        return (cond1 or cond2)

    def _3_check(self, x, y):
        """
        Checks if it is possible to put a group of three, with one of the three seated
        at the coordinates x, y
        """
        # possible x starting positions are from range (x-3, x]
        for start_x in range(x, x-3, -1):
            # if any of the start positions are valid, return True
            if self._check_row(start_x, start_x+3, y):
                return True

        # if all possible start positions are not valid, return False
        return False

    def _make_row(self, start_x, size, y):
        """
        Returns a list of coord tuples that represent the seats at row y, 
        ranging from [start_x, start_x+size)
        """
        returnlist = []
        for offset in range(size):
            returnlist.append((start_x+offset, y))

        return returnlist

    def _make_box(self, start_x, start_y):
        """
        Returns a list of coord tuples that represent the seats in a 2-2 box
        with the upper left seat being at start_x, start_y 
        """
        return [(start_x, start_y), (start_x+1, start_y),
                (start_x, start_y+1), (start_x+1, start_y+1)]

    def _check_row(self, start_x, end_x, y):
        """
        Checks if all coords between range[start_x, end_x) at row y are empty seats
        """
        for i in range(start_x, end_x):
            # if any coords are not valid, return False
            if not self.seating.isemptyseat(i, y):
                return False
        return True

    def _check_box(self, start_x, start_y):
        """
        Checks if it is possible to put a group of four in a 2-2 box, with the top left corner 
        of the box being at start_x, start_y
        """
        box_coords = self._make_box(start_x, start_y)
        return self.seating.areemptyseats(box_coords)
    
    def _add_box(self, start_x, start_y, groupid):
        """
        Adds individuals from group groupid to the box where the top left corner is at start_x, start_y
        """
        box_coords = self._make_box(start_x, start_y)
        self.seating.add_many(box_coords, groupid)
        
    def _4_check(self, x, y):
        """
        Checks if it is possible to put a group of four, either a row or a 2-2 box, where one of the 
        four is at coordinates x, y
        """

        # specify the range of possible row starts
        for start_x in range(x, x-4, -1):
            # if any of these rows are possible we can return True
            if self._check_row(start_x, start_x+4, y):
                return True
        
        # specify the possible box upper-left start coordinates
        box_start_coords = [(x, y), (x-1, y), (x, y-1), (x-1, y-1)]
        for start in box_start_coords:
            # if any of these boxes are possible we can return True
            if self._check_box(start[0], start[1]):
                return True

        return False 

    def _4_placement_valid_coords(self, x, y):
        """
        Returns possible rows and boxes where a group of four can be placed.

        This function is a bit over-complicated - I made it when I was first thinking of this
        problem, but came across more elegant solutions later that don't need this function
        """
        valid_rows = []
        valid_boxes = []
        
        # check possible rows
        for start_x in range(x, x-4, -1):
            if self._check_row(start_x, start_x+4, y):
                valid_rows.append(self._make_row(start_x, 4, y))
        
        # check possible boxes
        box_start_coords = [(x, y), (x-1, y), (x, y-1), (x-1, y-1)]
        for start in box_start_coords:
            x, y = start[0], start[1]
            if self._check_box(x, y): # if box is valid
                valid_boxes.append(self._make_box(x, y))
        return valid_rows, valid_boxes

    def _3_placement_valid_coords(self, x, y):
        """
        Returns possible rows where a group of three can be placed.
        """
        valid_rows = []
        for start_x in range(x, x-3, -1):
            if self._check_row(start_x, start_x+3, y): # if row is valid
                valid_rows.append(self._make_row(start_x, 3, y))
        return valid_rows

class NaiveSolver(BaseSolver):
    """
    A naive solver that selects coordinates at random and tries to add a group at 
    that location, until all groups have been added. 

    Useful as a baseline but not good. Also outlines the basic logic flow of a solver
    """
    def solve(self):
        """
        Naively solves by selecting a coordinate at random from the empty coordinates, 
        and tries to add a group with one member of the group at that coordinate. 

        This is an ugly function, but I'm leaving it as is because it's how I originally
        coded it up and this is supposed to be a naive implementation. See ExhaustiveGreedySolver
        for a cleaner code solver. 
        """
        
        # we must specify groupids to know which individual belongs to which group later
        # we initialize with 1 and increment. 
        groupid = 1

        # main flow is a while loop that ends when the attendees have all been placed
        while not self.attendees.check_complete():

            # select the largest group
            curr = self.attendees.pop_largest()

            # select a random coordinate that has an empty seat            
            coords = random.choice(tuple(self.seating.emptyseatcoords))

            # remember which seats we couldn't add this group at
            failed_seats = set()

            # if we can add this group, continue, but if we cannot, we keep 
            # trying to select new coordinates. 
            while not self._group_here_ok(curr, coords[0], coords[1]):
                failed_seats.add(coords)

                # if we have run out of empty seats, we will know when 
                # we have as many unique failed seats as empty seat coordinates
                if len(failed_seats) == len(self.seating.emptyseatcoords):
                    # this means we cannot place this group at all, so raise an error
                    raise RuntimeError

                # otherwise, keep trying to select a seat at random. 
                coords = random.choice(tuple(self.seating.emptyseatcoords))
            
            # now, coords is a valid place to start. 
            x, y = coords[0], coords[1]

            # simple case, add the person to this spot
            if curr == 1:
                self.seating.add_person(x, y, groupid)
            
            if curr == 2:
                # we know at least this coord is valid
                self.seating.add_person(x, y, groupid)
                # now try to add to the right
                if self.seating.isemptyseat(x+1, y):
                    self.seating.add_person(x+1, y, groupid)
                # since there was a valid placement (because _group_here_ok passed)
                # we know we must be able to place to the left
                else:
                    self.seating.add_person(x-1, y, groupid)

            if curr == 3:
                # again, add to this coordinate
                self.seating.add_person(x, y, groupid)
                # if both seats to the right are free, add there
                if self.seating.isemptyseat(x+1, y) and self.seating.isemptyseat(x+2, y):
                    self.seating.add_person(x+1, y, groupid)
                    self.seating.add_person(x+2, y, groupid)
                # else if one seat to the right and one seat to the left is free
                elif self.seating.isemptyseat(x+1, y) and self.seating.isemptyseat(x-1, y):
                    self.seating.add_person(x+1, y, groupid)
                    self.seating.add_person(x-1, y, groupid)
                else: # both seats to the left must be free
                    self.seating.add_person(x-1, y, groupid)
                    self.seating.add_person(x-2, y, groupid)

            if curr == 4:
                # separate function for placement
                self._4_place(x, y, groupid)
            
            groupid += 1

    def _4_place(self, x, y, groupid):
        """
        Function to handle placement of a group of four in a row or box, with one person at x, y
        """
        # first we check rows
        for start_x in range(x, x-4, -1): # for all possible row starts
            if self._check_row(start_x, start_x+4, y): # if this row is valid
                # add it and terminate
                self.seating.add_many(self._make_row(start_x, 4, y), groupid)
                return

        # if no rows were valid, we check boxes
        box_start_coords = [(x, y), (x-1, y), (x, y-1), (x-1, y-1)]
        for x, y in box_start_coords:
            if self._check_box(x, y): # if this box is valid
                # add this box and terminate
                self._add_box(x, y, groupid)
                return

class PrioritySolver(BaseSolver):
    """
    A solver that maintains a map that stores the distance to the nearest occupied
    seat for each coordinate, and a max heap that yields the coordinate that has a 
    seat that is furthest from an occupied seat. 
    """
    def solve(self, order='descending'):
        """
        Solves by trying to place a group with one person seated at the seat yielded
        by the max heap. If not possible at this seat, tries the next best seat. 

        Also allows for different ways to select the attendees, including by 
        descending group size, ascending group size, or randomly. 

        Once a valid seat has been found add at, we add the rest of the group members 
        to the arrangement that maximizes distance to other occupied seats
        """
        # heapify the coordinates and initialize the dist_map and groupid
        self._heapify_coords()
        self.dist_map = copy.copy(self.seating.seating)
        groupid = 1

        # while not everyone has been placed
        while not self.attendees.check_complete():
            # select the next group to add
            if order == 'descending':
                curr = self.attendees.pop_largest()
            elif order == 'ascending':
                curr = self.attendees.pop_smallest()
            elif order == 'random':
                curr = self.attendees.pop_random()

            # take the best coordinate
            _, coords = self.coordheap.pop()

            # initialize failed_seats
            failed_seats = set()

            # re-add the seats that were popped while trying to find
            # a valid start_coordinate back to the heap at the end. 
            # Those coords are saved here
            to_push_end = []
            
            # if we can add this group, continue, but if we cannot, we keep 
            # trying to select new coordinates. 
            while not self._group_here_ok(curr, coords[0], coords[1]):
                failed_seats.add(coords)
                if len(failed_seats) == len(self.seating.emptyseatcoords):
                    raise RuntimeError

                # save the coordinates that were popped before getting the next 
                # best coordinate
                to_push_end.append((coords))
                _, coords = self.coordheap.pop()
            

            x, y = coords[0], coords[1]
            if curr == 1:
                self.seating.add_person(x, y, groupid)
            elif curr == 2:
                self.seating.add_person(x, y, groupid)
                 # add to the better of the two possible locations
                next_x, next_y = self._2_best(x, y)
                self.seating.add_person(next_x, next_y, groupid)
            elif curr == 3:
                # add to the best row including this seat
                next_adds = self._3_best(x, y)
                self.seating.add_many(next_adds, groupid)
            elif curr == 4:
                # add to the best row or box including this seat
                four_add = self._4_best(x, y)
                self.seating.add_many(four_add, groupid)
            
            # update the distmap, this will also mean the priorities
            # in our heap must be updated
            heap_updates = self._update_distmap()

            # apply both the heap updates and return the coordinates that were popped
            # while looking for a valid group placement area, back to the heap
            self._update_coordheap(heap_updates, to_push_end)
            groupid += 1

    def _heapify_coords(self):
        """
        Initialize the max priority heap with the empty seat coordinates. 
        All seats start with the same priority of 0.
        """
        coordheap = MaxHeap()
        for coord in self.seating.emptyseatcoords:
            coordheap.push(0, coord)
        self.coordheap = coordheap

    def _update_distmap(self):
        """
        Function that updates the distance map, after the group has been placed. 

        This requires the following steps:
            Get all seats and make a pairwise distance matrix between the seats
            Get coordinates of all empty seats (these are the seats that need updating)
            Update the distmap at the empty seats if there is a new occupied seat that
                 is closer
            Return a dict of updates to be made to the coordheap
        """
        # get all seats
        all_seats = np.where(self.seating.seating != -1) # we don't care about aisles heres
        all_seats = [(x, y) for x, y in zip(all_seats[0], all_seats[1])]
        all_seats = np.array(all_seats)

        # if the Seating we are using specifies non-unit height and width of seats, 
        # we must modify the (x, y) coordinates of the seats accordingly. 
        if 'seatlen' in self.seating.__dict__.keys():
            # since the coordinates in all_seats are currently in unit-scale, 
            # we need to just multiply by the actual seatlen and seatwidth to get
            # the new coordinate system
            all_seats[:, 0] = all_seats[:, 0] * self.seating.seatwidth
            all_seats[:, 1] = all_seats[:, 1] * self.seating.seatlen

        dmat = squareform(pdist(all_seats))

        # We only want to update the free seats
        free_seats = np.where(self.seating.seating == 0)
        free_seats = set((x, y) for x, y in zip(free_seats[0], free_seats[1]))

        # all changes to the distmap also need to be changed in the coordheap
        # stash the changes here and return at the end
        coordheap_updates = {}

        # we loop over all the seats, getting both the seat coordinates in unit-scale
        # and the row in the pairwise distance matrix
        for (x, y), row in zip(all_seats, dmat):
            if (x, y) in free_seats: # do nothing otherwise
                # looping over the neighboring seats in order of increasing distance
                ranking = np.argsort(row)
                for rank in ranking[1:]: # because 0th will be self

                    # if this neighboring seat is empty, continue
                    if self.seating.isemptyseat(all_seats[rank][0], all_seats[rank][1]):
                        continue

                    # if this seat is occupied but the same distance is already present 
                    # in the distmap, move on to the next free seat.
                    elif row[rank] == self.dist_map[x, y]:
                        break

                    # otherwise, we have a new nearest seat and must update 
                    # the distmap and coordheap accordingly, then exit the loop
                    else:
                        self.dist_map[x, y] = row[rank] # update the distmap with the new dist
                        coordheap_updates[(x, y)] = row[rank]
                        break

        # at the end we return the coordheap updates
        return coordheap_updates

    def _update_coordheap(self, updates, to_push_end):
        """
        Function that updates the coordheap
            - changing priorities due to added individuals
            - re-adding the coordinates that were popped while trying
                to find a valid starting coordinate
        """
        # the update value should be in updates[coords]
        for i in range(len(self.coordheap)):
            coords = self.coordheap[i][1]
            if coords in updates.keys():
                self.coordheap[i] = (updates[coords], coords)
        # updating the values manually means we need to restore the heap state
        self.coordheap.heapify()
        
        for x, y in to_push_end:
            self.coordheap.push(self.dist_map[x, y], (x, y))

    def _2_best(self, x, y):
        """
        Function that finds the best way to place a second person 
        next to x, y
        """
        # if left is empty or right is empty, seat defaults to the other
        if self.seating.isemptyseat(x+1, y) and not self.seating.isemptyseat(x-1, y):
            return x+1, y
        elif self.seating.isemptyseat(x-1, y) and not self.seating.isemptyseat(x+1, y):
            return x-1, y
        # otherwise, select the seat that has a higher dist_map value
        elif self.dist_map[x+1, y] > self.dist_map[x-1, y]:
            return x+1, y
        else: # self.dist_map[x-1, y] >= self.dist_map[x+1, y]
            return x-1, y

    def _3_best(self, x, y):
        """
        Function that returns the best coordinates to place three people, including a person
        at x, y. 
        """
        valid_rows = self._3_placement_valid_coords(x, y) # returns all valid triplets 
        
        # selects the triplet that had the farthest average distance
        row_means = [self.get_avg_dist(validrow) for validrow in valid_rows]
        best_row = np.argmax(row_means)
        return valid_rows[best_row]

    def get_avg_dist(self, coord_set):
        """
        Returns the average distance score of the coordinates in the coord_set
        """
        dists = []
        for x, y in coord_set:
            dists.append(self.dist_map[x, y])
        return np.mean(dists)


    def _4_best(self, x, y):
        """
        Function that returns the best coordinates to place four people, in either 
        a row or a 2-2 box, including a person at x, y
        """
        # get all valid rows and boxes
        valid_rows, valid_boxes = self._4_placement_valid_coords(x, y)
        
        # get the best valid box, if there were no valid rows
        if len(valid_rows) == 0:
            box_means = [self.get_avg_dist(validbox) for validbox in valid_boxes]
            best_box = np.argmax(box_means)
            return valid_boxes[best_box]
        # get the best valid row, if there were no valid boxes
        elif len(valid_boxes) == 0:
            row_means = [self.get_avg_dist(validrow) for validrow in valid_rows]
            best_row = np.argmax(row_means)
            return valid_rows[best_row]
        # get the best row or box
        else:
            row_means = [self.get_avg_dist(validrow) for validrow in valid_rows]
            box_means = [self.get_avg_dist(validbox) for validbox in valid_boxes]

            best_row = np.argmax(row_means)
            best_box = np.argmax(box_means)

            if row_means[best_row] > box_means[best_box]:
                return valid_rows[best_row]
            else:
                return valid_boxes[best_box]

class ExhaustiveGreedySolver(PrioritySolver):
    """
    This solver simplifies the PrioritySolver by not using a heap to get 
    the best starting coordinates, instead trying every possible position for 
    a given group, computing the average distance for the valid positions, and 
    then selecting the position that has the greatest average distance. 

    It is Exhaustive because it tries every possible position, and Greedy because 
    it always picks the best possible position for the current group. 
    """

    def solve(self, order='descending'):
        """
        Function that solves the seating by greedily picking the best location
        for a given group. 
        """

        # initialize dist_map
        self.dist_map = copy.deepcopy(self.seating.seating)
        groupid = 1

        # while there are attendees left to seat
        while not self.attendees.check_complete():
            # pop a group
            if order == 'descending':
                curr = self.attendees.pop_largest()
            elif order == 'ascending':
                curr = self.attendees.pop_smallest()
            elif order == 'random':
                curr = self.attendees.pop_random()

            # check every possible position for the group
            if curr == 1:
                self._add_one(groupid)
            elif curr == 2:
                self._add_two(groupid)
            elif curr == 3:
                self._add_three(groupid)
            elif curr == 4:
                self._add_four(groupid)
            
            # update distmap to reflect added group, can ignore  
            # the coordheap updates
            _ = self._update_distmap()
            groupid += 1

    def _add_one(self, groupid):
        """
        Function that finds the best coordinates to seat a single person,
        and seats the person at this location
        """
        coordlist = [] # valid locations
        distlist = [] # distance at each valid location
        
        # build up these lists
        for x, y in self.seating.emptyseatcoords:
            coordlist.append((x, y))
            distlist.append(self.dist_map[x, y])
        
        # finds the best coordinate and seats the person there
        best_x, best_y = coordlist[np.argmax(distlist)]

        # However if we are placing the first group, we will pick the set of
        # valid coordinates, which are as close to 0, 0 as possible
        if groupid == 1:
            sums = [np.array(coords).sum() for coords in coordlist]
            best_x, best_y = coordlist[np.argmin(sums)]

        self.seating.add_person(best_x, best_y, groupid)
    
    def _add_two(self, groupid):
        """
        Function that finds the best position to seat two people, and 
        seats these people at this position.
        """
        coordlist = [] # valid positions
        distlist = [] # sum of distances for this position
        
        # build up these lists
        for x, y in self.seating.emptyseatcoords:
            # just need to check if seat to the right is empty, 
            # since if seat to the left is empty, this pair will be included
            # when x, y is the seat to the left. 
            if (x+1, y) in self.seating.emptyseatcoords:
                coordlist.append([(x, y), (x+1, y)])
                distlist.append(self.dist_map[x, y] + self.dist_map[x+1, y])
        
        # selects the best position with highest distance, and seats the people there
        best_coords = coordlist[np.argmax(distlist)]

        # However if we are placing the first group, we will pick the set of
        # valid coordinates, which are as close to 0, 0 as possible
        if groupid == 1:
            sums = [np.array(coords).sum() for coords in coordlist]
            best_coords = coordlist[np.argmin(sums)]

        self.seating.add_many(best_coords, groupid)

    def _add_three(self, groupid):
        """
        Function that finds the best position to seat three people, and 
        seats these people at this position.
        """
        coordlist = [] # valid positions
        distlist = [] # sum of distances for this position

        for x, y in self.seating.emptyseatcoords:
            # similar to add_two, just need to check if the two seats to the right are open
            cond1 = (x+1, y) in self.seating.emptyseatcoords
            cond2 = (x+2, y) in self.seating.emptyseatcoords
            if cond1 and cond2:
                # add to the coordlist and distlist
                coordlist.append([(x, y), (x+1, y), (x+2, y)])
                distlist.append(self.dist_map[x, y] + self.dist_map[x+1, y] + self.dist_map[x+2, y])
        
        # select best position with highest distance, seats the group there
        best_coords = coordlist[np.argmax(distlist)]

        # However if we are placing the first group, we will pick the set of
        # valid coordinates, which are as close to 0, 0 as possible
        if groupid == 1:
            sums = [np.array(coords).sum() for coords in coordlist]
            best_coords = coordlist[np.argmin(sums)]

        self.seating.add_many(best_coords, groupid)

    def _add_four(self, groupid):
        """
        Function that finds the best position to seat four people, and 
        seats these people at this position.
        """
        coordlist = [] # valid positions
        distlist = [] # sum of distances for this position

        for x, y in self.seating.emptyseatcoords:
            # checking if rows and boxes are valid, adding them and their distances if they are
            if self._check_row(x, x+4, y):
                coordlist.append(self._make_row(x, 4, y))
                distlist.append(self.dist_map[x, y] + self.dist_map[x+1, y] + self.dist_map[x+2, y] + self.dist_map[x+3, y])
            if self._check_box(x, y):
                coordlist.append(self._make_box(x, y))
                distlist.append(self.dist_map[x, y] + self.dist_map[x+1, y] + self.dist_map[x, y+1] + self.dist_map[x+1, y+1])

        # selecting best position and seating group at this position.
        best_coords = coordlist[np.argmax(distlist)]

        # However if we are placing the first group, we will pick the set of
        # valid coordinates, which are as close to 0, 0 as possible
        if groupid == 1:
            sums = [np.array(coords).sum() for coords in coordlist]
            best_coords = coordlist[np.argmin(sums)]

        self.seating.add_many(best_coords, groupid)


            

        


