from Attendees import BaseAttendees
from Seating import BaseSeating, LengthWidthSeating
from Solvers import NaiveSolver, PrioritySolver, ExhaustiveGreedySolver
from evaluate import evaluate_nearest_distance
from evaluate import evaluate_closerthan_thresh
import copy

seating = LengthWidthSeating.from_json('testseating.json')
print(seating.seating.T)
print('##########')
print('naive')


attendees = BaseAttendees.from_uniform(seating.unfilledseats / 2, 5)
attendeescopy = copy.deepcopy(attendees)
attendeescopy2 = copy.deepcopy(attendees)

solver = NaiveSolver(seating, attendees)
solver.solve()
print(seating.seating.T)
print(evaluate_nearest_distance(seating))
print(evaluate_closerthan_thresh(seating, 1.5))
print('##########')
print('priority')

seating = LengthWidthSeating.from_json('testseating.json')
solver = PrioritySolver(seating, attendeescopy)
solver.solve()
print(seating.seating.T)
print(evaluate_nearest_distance(seating))
print(evaluate_closerthan_thresh(seating, 1.5))
print('##########')
print('exhaustive')
seating = LengthWidthSeating.from_json('testseating.json')
solver = ExhaustiveGreedySolver(seating, attendeescopy2)
solver.solve()
print(seating.seating.T)
print(evaluate_nearest_distance(seating))
print(evaluate_closerthan_thresh(seating, 1.5))