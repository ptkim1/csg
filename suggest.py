# Given approximate expected Attendee distribution and a Seating, suggest number of seats to make available
import numpy as np
from Solvers import ExhaustiveGreedySolver
from Attendees import BaseAttendees
import copy
from evaluate import evaluate_closerthan_thresh

class Search():
    def __init__(self, min_, max_):
        self.min_ = min_
        self.max_ = max_
    
    def first(self):
        self.last = (self.max_ + self.min_) / 2
        return round(self.last)

    def more(self):
        self.min_ = self.last
        self.last = (self.max_ + self.min_) / 2
        return round(self.last)
    
    def less(self):
        self.max_ = self.last
        self.last = (self.max_ + self.min_) / 2
        return round(self.last)
    
    def converged_initial(self):
        diff = self.max_ - self.min_
        if diff < 5:
            return True
        else:
            return False

def check_pass(runs, tolerance):
    if percent_failed(runs) <= tolerance:
        return True
    else:
        return False

def n_failures(runs):
    runs = np.array(runs).astype(int)
    return len(runs) - sum(runs)

def percent_failed(runs):
    runs = np.array(runs).astype(int)
    return 1 - (sum(runs) / len(runs))

def suggest_n_tickets(expected_attendee_dist, seating, bootstrap_samples, threshold=1.5, tolerance=0.05, verbose=True):
    search = Search(0, seating.nseats())
    n_attendees = search.first()

    while not search.converged_initial():
        if verbose:
            print('searching, {} attendees'.format(n_attendees))
        if is_safe(expected_attendee_dist, copy.deepcopy(seating), n_attendees, bootstrap_samples, threshold, tolerance):
            n_attendees = search.more()
        else:
            n_attendees = search.less()

    if verbose:
        print('initial convergence, search min = {}, search max = {}'.format(round(search.min_), round(search.max_)))

    # now we've converged, let's check the values between convergence
    for proposed_n_attendees in range(int(search.max_) + 1, 0, -1):
        print('testing {} attendees'.format(proposed_n_attendees))
        if is_safe(expected_attendee_dist, copy.deepcopy(seating), proposed_n_attendees, bootstrap_samples, threshold, tolerance):
            return proposed_n_attendees


# Given expected Attendee distribution, seating, and a number of tickets to allow, report whether this is safe. 
def is_safe(expected_attendee_dist, seating, ticket_count, bootstrap_samples, threshold, tolerance, verbose=True, earlystop=25):
    def run_test():
        attendees = BaseAttendees.from_probs(expected_attendee_dist, ticket_count)
        test_seating = copy.deepcopy(seating)
        solver = ExhaustiveGreedySolver(test_seating, attendees)
        solver.solve()
        good = evaluate_closerthan_thresh(test_seating, threshold, 'boolean')
        return good
    
    runs = []
    for i in range(0, bootstrap_samples):
        good = run_test()
        if verbose and not good:
            print('run {} of {} failed'.format(i+1, bootstrap_samples))

        runs.append(good)

        if earlystop and earlystop-1 == i and not check_pass(runs, tolerance*2):
            print('stopping early with {} of {} failures'.format(n_failures(runs), earlystop))
            return False
        
    if check_pass(runs, tolerance):
        if verbose:
            print('{} tickets succeeds with {} / {} failures'.format(ticket_count, n_failures(runs), bootstrap_samples))
        return True
    else:
        if verbose:
            print('{} tickets fails with {} / {} failures'.format(ticket_count, n_failures(runs), bootstrap_samples))
        return False
