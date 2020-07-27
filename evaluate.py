import numpy as np
from Seating import BaseSeating
from scipy.spatial.distance import pdist, squareform
import copy

"""
Evaluation is based on average distance to nearest person
not in the same group
"""

def get_occupied_seats(seating: BaseSeating):
    occupied_seats = np.where(seating.seating > 0)
    occupied_seats = [[x, y] for x, y in zip(occupied_seats[0], occupied_seats[1])]
    occupied_seats = np.array(occupied_seats)
    return occupied_seats

def get_dmat_seats(occupied_seats, seating):
    adjusted_seats = copy.copy(occupied_seats)
    if 'seatlen' in seating.__dict__.keys():
        adjusted_seats[:, 0] = adjusted_seats[:, 0] * seating.seatwidth
        adjusted_seats[:, 1] = adjusted_seats[:, 1] * seating.seatlen
    return squareform(pdist(adjusted_seats))

def evaluate_nearest_distance(seating: BaseSeating):
    distances = []
    
    occupied_seats = get_occupied_seats(seating)
    dmat = get_dmat_seats(occupied_seats, seating)

    for i, row in enumerate(dmat):
        curr_groupid = seating.seating[occupied_seats[i][0], occupied_seats[i][1]] # gets current group id
        ranking = np.argsort(row) 

        for rank in ranking[1:]: # because 0th will be self
            coords_other = occupied_seats[rank] # gets coords of closest
            if curr_groupid == seating.seating[coords_other[0], coords_other[1]]: # if seat in same group
                continue
            distances.append(row[rank])
            break

    return np.mean(distances)

def evaluate_closerthan_thresh(seating: BaseSeating, threshold):
    number_below_thresh = []
    
    occupied_seats = get_occupied_seats(seating)
    dmat = get_dmat_seats(occupied_seats, seating)

    for i, row in enumerate(dmat):
        curr_groupid = seating.seating[occupied_seats[i][0], occupied_seats[i][1]]
        ranking = np.argsort(row)

        curr_count = 0
        for rank in ranking[1:]:
            if row[rank] > threshold:
                number_below_thresh.append(curr_count)
                break

            coords_other = occupied_seats[rank]
            if curr_groupid == seating.seating[coords_other[0], coords_other[1]]:
                continue
            curr_count += 1
    
    return np.mean(number_below_thresh)

            

    



