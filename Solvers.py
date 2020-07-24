from Seating import BaseSeating
from Attendees import BaseAttendees
from abc import abstractmethod
import numpy as np
import random
from heapq import heappush, heappop, heapify
import copy
from scipy.spatial.distance import pdist, squareform


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

    def _4_placement_valid_coords(self, x, y):
        valid_rows = []
        valid_boxes = []
        for start_x in range(x, x-4):
            if self._check_row(start_x, start_x+4, y):
                valid_rows.append([(start_x, y), (start_x+1, y), (start_x+2, y), (start_x+3, y)])
        
        box_start_coords = [(x, y), (x-1, y), (x, y-1), (x-1, y-1)]
        for start in box_start_coords:
            x, y = start[0], start[1]
            if self._check_box(x, y):
                valid_boxes.append([(x, y), (x+1, y), (x, y+1), (x+1, y+1)])
        return valid_rows, valid_boxes
    
       

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
        self.dist_map = copy.copy(self.seating.seating) # when placing an additional group member, we'll have to check for if it's a valid seat or not
        groupid = 1

        while not self.attendees.check_complete():
            curr = self.attendees.pop_largest()
            invdist, coords = heappop(self.coordheap)
            failed_seats = set()
            to_push_end = []
            
            # I think tryplacegroup is not working as intended
            # also we need to update the coords that we save to push later in to_push_end
            while not self._tryplacegroup(curr, coords[0], coords[1]):
                failed_seats.add(coords)
                if len(failed_seats) == len(self.seating.emptyseatcoords):
                    raise RuntimeError
                    # raise an error - no valid placements
                to_push_end.append((invdist, coords))
                invdist, coords = heappop(self.coordheap)
            
            x, y = coords[0], coords[1]
            if curr == 1:
                self.seating.add_person(x, y, groupid)
            elif curr == 2:
                self.seating.add_person(x, y, groupid)
                next_x, next_y = self._2_best(x, y)
                self.seating.add_person(next_x, next_y, groupid)
            elif curr == 3:
                self.seating.add_person(x, y, groupid)
                next_adds = self._3_best(x, y)
                self.seating.add_many(next_adds, groupid)
            elif curr == 4:
                four_add = self._4_best(x, y)
                self.seating.add_many(four_add, groupid)
            
            
            heap_updates = self._update_distmap()
            self._update_coordheap(heap_updates, to_push_end)
            groupid += 1
            print(groupid)
            print(self.seating.seating.T)
            # print(self.dist_map.T)

    def _heapify_coords(self):
        coordheap = []
        for coord in self.seating.emptyseatcoords:
            heappush(coordheap, (0, coord))
        self.coordheap = coordheap

    def _update_distmap(self):
        # get all seats
        # get empty seats
        # get pdistmat
        # for empty seats, update invdistmap
        # return a dict of updates to be made to the coordheap
        all_seats = np.where(self.seating.seating != -1)
        all_seats = [(x, y) for x, y in zip(all_seats[0], all_seats[1])]

        free_seats = np.where(self.seating.seating == 0)
        free_seats = set((x, y) for x, y in zip(free_seats[0], free_seats[1]))

        dmat = squareform(pdist(all_seats))

        coordheap_updates = {}

        for seat, row in zip(all_seats, dmat):
            if seat in free_seats:
                x, y = seat[0], seat[1]
                ranking = np.argsort(row)
                for rank in ranking[1:]: # because 0th will be self
                    if self.seating.isemptyseat(all_seats[rank][0], all_seats[rank][1]):
                        continue
                    elif row[rank] == self.dist_map[x, y]:
                        break
                        # still the same seat is nearest
                    else:
                        self.dist_map[x, y] = row[rank]
                        coordheap_updates[(x, y)] = row[rank]
                        break
                        # update the invdist_map
                        # add to dict to update the coordheap
                        # exit the loop
        return coordheap_updates

    def _update_coordheap(self, updates, to_push_end):
        for i in range(len(self.coordheap)):
            coords = self.coordheap[i][1]
            if coords in updates.keys():
                new_invdist = -1 * updates[coords]
                self.coordheap[i] = (new_invdist, coords)
        heapify(self.coordheap)

        [heappush(self.coordheap, to_push) for to_push in to_push_end]

    def _2_best(self, x, y):
        if self.seating.isemptyseat(x+1, y) and not self.seating.isemptyseat(x-1, y):
            return x+1, y
        elif self.seating.isemptyseat(x-1, y) and not self.seating.isemptyseat(x+1, y):
            return x-1, y
        elif self.dist_map[x+1, y] > self.dist_map[x-1, y]:
            return x+1, y
        else: # self.dist_map[x-1, y] >= self.dist_map[x+1, y]
            return x-1, y

    def _3_best(self, x, y):
        return_coords = []
        if not self.seating.isemptyseat(x+1, y):
            return_coords.extend([(x-1, y), (x-2, y)])
        elif not self.seating.isemptyseat(x-1, y):
            return_coords.extend([(x+1, y), (x+2, y)])
        elif self.dist_map[x+1, y] > self.dist_map[x-1, y]:
            return_coords.append((x+1, y))
            if self.dist_map[x+2, y] > self.dist_map[x-1, y]:
                return_coords.append((x+2, y))
            else:
                return_coords.append((x-1, y))
        
        elif self.dist_map[x-1, y] >= self.dist_map[x+1, y]:
            return_coords.append((x-1, y))
            if self.dist_map[x-2, y] > self.dist_map[x+1, y]:
                return_coords.append((x-2, y))
            else:
                return_coords.append((x+1, y))

        return return_coords

    def get_avg_dist(self, coord_set):
        dists = []
        for coord in coord_set:
            dists.append(self.dist_map[coord[0], coord[1]])
        return np.mean(dists)


    def _4_best(self, x, y):
        valid_rows, valid_boxes = self._4_placement_valid_coords(x, y)
        
        if len(valid_rows) == 0:
            box_means = [self.get_avg_dist(validbox) for validbox in valid_boxes]
            best_box = np.argmin(box_means)
            return valid_boxes[best_box]
        elif len(valid_boxes) == 0:
            row_means = [self.get_avg_dist(validrow) for validrow in valid_rows]
            best_row = np.argmin(row_means)
            return valid_rows[best_row]
        else:
            row_means = [self.get_avg_dist(validrow) for validrow in valid_rows]
            box_means = [self.get_avg_dist(validbox) for validbox in valid_boxes]

            best_row = np.argmin(row_means)
            best_box = np.argmin(box_means)

            if row_means[best_row] < box_means[best_box]:
                return valid_rows[best_row]
            else:
                return valid_boxes[best_box]

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

