from Seating import BaseSeating
from Attendees import BaseAttendees
from abc import abstractmethod
import numpy as np
import random
from heapq import heappush, heappop
import copy

class BaseSolver:
    def __init__(self, seating: BaseSeating, attendees: BaseAttendees):
        self.seating = seating
        self.attendees = attendees
        # self.valid_coords = np.array([x, y] for x, y in zip(seating.))

    @abstractmethod
    def solve(self):
        pass

    def _group_here_ok(self, group, x, y):
        selection = {
            1: self._1_check,
            2: self._2_check,
            3: self._3_check,
            4: self._4_check # ,
        #     5: self._5_check,
        #     6: self._6_check,
        #     7: self._7_check,
        #     8: self._8_check,
        #     9: self._9_check
        }

        return selection[group](x, y)

    def _1_check(self, x, y):
        return self.seating.isemptyseat(x, y)
    
    def _2_check(self, x, y):
        return (self.seating.isemptyseat(x, y) and (self.seating.isemptyseat(x+1, y) or self.seating.isemptyseat(x-1, y)))

    def _3_check(self, x, y):
        if not self.seating.isemptyseat(x, y):
            return False
        elif self.seating.isemptyseat(x+1, y):
            if self.seating.isemptyseat(x-1, y) or self.seating.isemptyseat(x+2, y):
                return True
        elif self.seating.isemptyseat(x-1, y) and self.seating.isemptyseat(x-2, y):
            return True
        else: 
            return False

    def _check_row(self, start_x, end_x, y):
        for i in range(start_x, end_x):
            if not self.seating.isemptyseat(i, y):
                return False
        return True

    def _check_box(self, start_x, start_y):
        box_coords = [(start_x, start_y), (start_x+1, start_y), (start_x, start_y+1), (start_x+1, start_y+1)]
        return self.seating.areemptyseats(box_coords)
        
    def _4_check(self, x, y):
        for start_x in range(x, x-4):
            if self._check_row(start_x, start_x+4, y):
                return True
        box_start_coords = [(x, y), (x-1, y), (x, y-1), (x-1, y-1)]
        for start in box_start_coords:
            if self._check_box(start[0], start[1]):
                return True
        return False 

    
       

class NaiveSolver(BaseSolver):
    # adds randomly 
    def solve(self):
        groupid = 1

        while not self.attendees.check_complete():
            curr = self.attendees.pop_largest()            
            coords = random.choice(tuple(self.seating.emptyseatcoords))
            failed_seats = set()
            while not self._tryplacegroup(curr, coords[0], coords[1]):
                failed_seats.add(coords)
                if len(failed_seats) == len(self.seating.emptyseatcoords):
                    raise RuntimeError
                    # raise an error - no valid placements
                coords = random.choice(tuple(self.seating.emptyseatcoords))
            
            x, y = coords[0], coords[1]
            # so we found a valid place to start.
            if curr >= 1:
                self.seating.add_person(x, y, groupid)
            if curr == 2:
                # try to add a person to the left or right
                if self.seating.isemptyseat(x+1, y):
                    self.seating.add_person(x+1, y, groupid)
                else:
                    # must have been a free seat to the other side
                    self.seating.add_person(x-1, y, groupid)
            if curr == 3:
                if self.seating.isemptyseat(x+1, y) and self.seating.isemptyseat(x+2, y):
                    self.seating.add_person(x+1, y, groupid)
                    self.seating.add_person(x+2, y, groupid)

                elif self.seating.isemptyseat(x+1, y) and self.seating.isemptyseat(x-1, y):
                    self.seating.add_person(x+1, y, groupid)
                    self.seating.add_person(x-1, y, groupid)
                
                else: # must be both left empty
                    self.seating.add_person(x-1, y, groupid)
                    self.seating.add_person(x-2, y, groupid)

            if curr == 4:
                self._4_place(x, y, groupid)
            
            groupid += 1

            
    def _tryplacegroup(self, group, x, y):
        coords = random.choice(tuple(self.seating.emptyseatcoords))
        if self._group_here_ok(group, coords[0], coords[1]):
            return True
        else:
            return False

    def _4_place(self, x, y, groupid):
        for start_x in range(x, x-4):
            if self._check_row(start_x, start_x+4, y):
                self.seating.add_many([(xcoord, ycoord) for xcoord, ycoord in zip(range(start_x, start_x+4), [y] * 4)], groupid)
                return
        box_start_coords = [(x, y), (x-1, y), (x, y-1), (x-1, y-1)]
        for start in box_start_coords:
            if self._check_box(start[0], start[1]):
                self._add_box(start[0], start[1], groupid)
                return
        
        raise RuntimeError 

    def _add_box(self, start_x, start_y, groupid):
        box_coords = [(start_x, start_y), (start_x+1, start_y), (start_x, start_y+1), (start_x+1, start_y+1)]
        self.seating.add_many(box_coords, groupid)

class PriorityMaxSolver(BaseSolver):
    # Plan is to maintain a score for each possible position
    # Based on how far it is to the nearest other person
    # Then take the best scoring position every time. 
    # Starts w/ groups from largest to smallest
    
    def solve(self):
        # step 1: get the allowed coordinates 
        self._heapify_coords()
        self.invdist_map = copy.copy(self.seating.seating)
        groupid = 0

        while not self.attendees.check_complete():
            curr = self.attendees.pop_largest()
            invdist, coords = heappop(self.coordheap)
            failed_seats = set()
            
            while not self._tryplacegroup(curr, coords[0], coords[1]):
                failed_seats.add(coords)
                if len(failed_seats) == len(self.seating.emptyseatcoords):
                    raise RuntimeError
                    # raise an error - no valid placements
                _next = heappop(self.coordheap)
                heappush(self.coordheap, (invdist, coords))
                invdist, coords = _next[0], _next[1]
            
            x, y = coords[0], coords[1]

            if curr >= 1:
                self.seating.add_person(x, y, groupid)
                self._update_invdistmap()
                


            


    def _heapify_coords(self):
        coordheap = []
        for coord in self.seating.emptyseatcoords:
            heappush(coordheap, (0, coord))
        self.coordheap = coordheap

    def _update_invdistmap(self):
        # get all seats
        # get empty seats
        # get pdistmat
        # for empty seats, update invdistmap and coordheap
        all_seats = 

        free_seats = np.where(self.seating.seating == 0)
        free_seats = [[x, y] for x, y in zip(free_seats[0], free_seats[1])]



    def _tryplacegroup(self, group, x, y):
        coords = random.choice(tuple(self.seating.emptyseatcoords))
        if self._group_here_ok(group, coords[0], coords[1]):
            return True
        else:
            return False

        # group placement: 
        # group of 2: side by side
        # group of 3: side by side
        # group of 4: square or row
        # group of 5: 3-2 or 2-3
        # group of 6: 3-3 or 4-2 or 2-2-2
        # group of 7: 3-4 or 4-3 or 2-2-3 or 2-3-2 or 3-2-2
        # group of 8: 4-4 or 3-3-2 or 3-2-3 or 2-3-3
        # group of 9: 3-3-3 only!
        # group of 10: 4-3-3- or 3-4-3 or 3-3-4

    