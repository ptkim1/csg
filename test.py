from Attendees import BaseAttendees
from Seating import BaseSeating
from Solvers import NaiveSolver, PriorityMaxSolver
from evaluate import evaluate_nearest_distance
from evaluate import evaluate_closerthan_thresh
import copy

seating = BaseSeating.from_json('testseating.json')
attendees = BaseAttendees.from_uniform(seating.unfilledseats / 3, 5)
attendeescopy = copy.deepcopy(attendees)
solver = NaiveSolver(seating, attendees)

print(seating.seating.T)
print('##########')
# solver = PriorityMaxSolver(seating, attendees)
solver.solve()


# need to make a function to display seatings in their proper transposed way
print(seating.seating.T)
# print(solver.dist_map.T)
print(evaluate_nearest_distance(seating))
print(evaluate_closerthan_thresh(seating, 1.5))

seating = BaseSeating.from_json('testseating.json')
solver = PriorityMaxSolver(seating, attendeescopy)
solver.solve()
print(seating.seating.T)
print(evaluate_nearest_distance(seating))
print(evaluate_closerthan_thresh(seating, 1.5))

# with open('test_results.txt', 'w') as f:
#     f.write(str(seating.seating))

