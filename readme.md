# Coronavirus Seating Generator

This repository is for Paul Kim's MSCB 02-601 Placement Project

## Goal: 
Given a number of attendees, who may be subdivided into groups, and a fixed seating block, seat the attendees in a way to maximize the distance between individuals from different groups, while keeping groups together. 

## Organization
Seating.py and Attendees.py contain the classes that generates the fixed seating block, and the set of attendees, respectively. Both have various constructor class methods to generate different types of seatings and attendees. 

Solvers.py contains classes of BaseSolver objects, which take a ```BaseSeating``` and ```BaseAttendees``` as input and implement a ```solve()``` method that places all the attendees, if possible, into the seating. The best solver available is the ```ExhaustiveGreedySolver```. Currently, only groups of between 1-4 are supported, but extending this with the ```ExhaustiveGreedySolver``` would not be difficult. 

evaluate.py contains functions that can be used to evaluate the quality of a solved seating. ```evaluate_nearest_distance``` computes the average distance to the nearest out-of-group neighbor for each person in the seating, while ```evaluate_closerthan_thresh``` computes the number of times the seating has individuals who are closer together than a social distancing threshold distance. 

suggest.py contains functions that can be used to inform event or travel planning around coronavirus social distancing restrictions.

## Quick Start
#### Dependencies
python>=3.7, numpy>=1.5, scipy>=1.3
#### Compare Naive vs Priority vs Exhaustive solvers on a seating for a simplified plane at half capacity
```python
from Attendees import BaseAttendees
from Seating import BaseSeating
from Solvers import NaiveSolver, PrioritySolver, ExhaustiveGreedySolver
from evaluate import evaluate_nearest_distance, evaluate_closerthan_thresh
import copy

seating = BaseSeating.from_json('simple_plane.json')
attendees = BaseAttendees.from_uniform(n_attendees = seating.unfilledseats / 2, maximum=5)
attendees2 = copy.deepcopy(attendees) # since we need the same randomly generated attendees for the other solvers
attendees3 = copy.deepcopy(attendees)
print('empty seating')
seating.display() # see the empty seating without any attendees


solver = NaiveSolver(seating, attendees)
solver.solve()
print('Naive Solver:')
print('Average dist to nearest other-group passenger: {}'.format(evaluate_nearest_distance(seating)))
print('Average number of threshold violations per person: {}'.format(evaluate_closerthan_thresh(seating, 1.5)))
seating.display()
print('\n')

seating = BaseSeating.from_json('simple_plane.json')
solver = PrioritySolver(seating, attendees2)
solver.solve()
print('Priority Solver:')
print('Average dist to nearest other-group passenger: {}'.format(evaluate_nearest_distance(seating)))
print('Average number of threshold violations per person: {}'.format(evaluate_closerthan_thresh(seating, 1.5)))
seating.display()
print('\n')

seating = BaseSeating.from_json('simple_plane.json')
solver = ExhaustiveGreedySolver(seating, attendees3)
solver.solve()
print('Exhaustive Greedy Solver:')
print('Average dist to nearest other-group passenger: {}'.format(evaluate_nearest_distance(seating)))
print('Average number of threshold violations per person: {}'.format(evaluate_closerthan_thresh(seating, 1.5)))
seating.display()
```

#### Suggest a number of tickets to offer for a small concert
```python
from Attendees import BaseAttendees
from Seating import BaseSeating
from Solvers import ExhaustiveGreedySolver
import suggest
from evaluate import evaluate_nearest_distance, evaluate_closerthan_thresh

expected_attendee_dist = {
    1: 1,
    2: 2,
    3: 2, 
    4: 1
}

seating = BaseSeating.from_json('smallconcertseating.json')
seating.display()
suggestion = suggest.suggest_n_tickets(expected_attendee_dist, seating,
                                       100, 1.5, 0.02)

attendees = BaseAttendees.from_probs(expected_attendee_dist, suggestion)
solver = ExhaustiveGreedySolver(seating, attendees)
solver.solve()
seating.display()
print('Average dist to nearest other-group passenger: {}'.format(evaluate_nearest_distance(seating)))
print('Average number of threshold violations per person: {}'.format(evaluate_closerthan_thresh(seating, 1.5)))
```
