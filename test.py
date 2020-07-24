from Attendees import BaseAttendees
from Seating import BaseSeating
from Solvers import NaiveSolver, PriorityMaxSolver
from evaluate import evaluate

seating = BaseSeating.from_json('testseating.json')
attendees = BaseAttendees.from_uniform(seating.unfilledseats / 2, 3)
solver = PriorityMaxSolver(seating, attendees)
solver.solve()


# need to make a function to display seatings in their proper transposed way
print(seating.seating.T)
# print(solver.dist_map.T)
print(evaluate(seating))

# with open('test_results.txt', 'w') as f:
#     f.write(str(seating.seating))

