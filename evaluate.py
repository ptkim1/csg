import numpy as np
from Seating import BaseSeating
from scipy.spatial.distance import pdist, squareform

"""
Evaluation is based on average distance to nearest person
not in the same group
"""



def evaluate(seating: BaseSeating):
    distances = []
    
    occupied_seats = np.where(seating.seating > 0)
    occupied_seats = [[x, y] for x, y in zip(occupied_seats[0], occupied_seats[1])]
    occupied_seats = np.array(occupied_seats)

    dmat = squareform(pdist(occupied_seats)) # gets a square distance matrix

    for i, row in enumerate(dmat):
        current_group = seating.seating[occupied_seats[i][0], occupied_seats[i][1]] # gets current group id
        ranking = np.argsort(row) 

        for rank in ranking[1:]: # because 0th will be self
            coords_other = occupied_seats[rank] # gets coords of closest
            if current_group == seating.seating[coords_other[0], coords_other[1]]: # if seat in same group
                continue
            distances.append(row[rank])
            break

    return np.mean(distances)

    
    



