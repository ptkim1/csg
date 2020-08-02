import numpy as np
from Seating import BaseSeating
from scipy.spatial.distance import pdist, squareform
import copy

"""
Functions for evaluation of solved seatings
"""

def get_occupied_seats(seating: BaseSeating):
    """
    Takes a solved seating and adds coordinates of all occupied seats to an array of size  
    (# occupied seats, 2)
    """
    occupied_seats = np.where(seating.seating > 0) # get occupied seats
    occupied_seats = [[x, y] for x, y in zip(occupied_seats[0], occupied_seats[1])] # convert to coords
    occupied_seats = np.array(occupied_seats) # convert to numpy array
    return occupied_seats

def get_dmat_seats(occupied_seats, seating):
    """
    Returns a square pairwise euclidean distance matrix between all occupied seats
    Can take into account non-unit seat dimensions
    """
    adjusted_seats = copy.copy(occupied_seats)
    if 'seatlen' in seating.__dict__.keys():
        adjusted_seats[:, 0] = adjusted_seats[:, 0] * seating.seatwidth
        adjusted_seats[:, 1] = adjusted_seats[:, 1] * seating.seatlen
    return squareform(pdist(adjusted_seats))

def evaluate_nearest_distance(seating: BaseSeating):
    """
    Takes a seating and returns the average distance between each individual x and the nearest other 
    individual y, where x and y belong to different groups
    """
    distances = []
    
    # get occupied seats and distance matrix
    occupied_seats = get_occupied_seats(seating)
    dmat = get_dmat_seats(occupied_seats, seating)

    
    for i, row in enumerate(dmat): # for individual i's pairwise distance to all other individuals
        # get the groupid of i
        curr_groupid = seating.seating[occupied_seats[i][0], occupied_seats[i][1]]

        # get the ranking that would sort the distances in increasing order
        ranking = np.argsort(row) 

        
        for rank in ranking[1:]: # because 0th will be self
            # occupied seats[rank] will be the coords of next closest invidiual to i
            coords_other = occupied_seats[rank] 

            # if they are in same group, check the next closest person
            if curr_groupid == seating.seating[coords_other[0], coords_other[1]]:
                continue
            
            # if they are in different groups, add this distance to our list of distances. 
            distances.append(row[rank])
            break
    
    return np.mean(distances)


def evaluate_closerthan_thresh(seating: BaseSeating, threshold, reduce_='mean'):
    """
    Takes a seating and counts the number of cases where two individuals from different groups
    are closer to each other than threshold. reduce_ is a string that specifies how to 
    return this information

    reduce:
        'mean' -> returns the average number of threshold violations
        'sum' -> returns the total number of threshold violations
        'boolean' -> returns False if the threshold was ever violated, True otherwise
    """
    number_below_thresh = []
    
    # get occupied seats and distance matrix
    occupied_seats = get_occupied_seats(seating)
    dmat = get_dmat_seats(occupied_seats, seating)


    for i, row in enumerate(dmat): # for individual i's pairwise distance to all other individuals
        # get the groupid of i
        curr_groupid = seating.seating[occupied_seats[i][0], occupied_seats[i][1]]
        
        # get the ranking that would sort the distances in increasing order
        ranking = np.argsort(row)

        curr_count = 0 # number of violations of threshold

        # now looping over the neighbors
        for rank in ranking[1:]:
            # if we are at a person who is farther than the threshold, we can exit the loop
            # since all subsequent people will be even farther
            if row[rank] > threshold:
                number_below_thresh.append(curr_count)
                break
            
            # if the other person is in the same group, continue
            coords_other = occupied_seats[rank]
            if curr_groupid == seating.seating[coords_other[0], coords_other[1]]:
                continue

            # if we have come this far, we have found a person who is in a different group
            # and closer than threshold, so we increment the count of threshold violations
            curr_count += 1
    
    # return the average or total number of violations, or a boolean that indicates 
    # whether all the distances between individuals from different groups were greater
    # than the threshold (a successful seating)
    if reduce_ == 'mean':
        return np.mean(number_below_thresh)
    elif reduce_ == 'sum':
        return sum(number_below_thresh)         
    elif reduce_ == 'boolean':
        if sum(number_below_thresh) == 0:
            return True
        else:
            return False   

    



