import numpy as np
from Solvers import ExhaustiveGreedySolver
from Attendees import BaseAttendees
from Seating import BaseSeating
import copy
from evaluate import evaluate_closerthan_thresh

class Search():
    """
    A class that is used by suggest_n_tickets to search the space
    of possible n_attendees in binary-search style. 
    """
    def __init__(self, min_, max_):
        """
        Initialize the search with the minimum and maximum possible n_attendees.
        """
        self.min_ = min_
        self.max_ = max_
    
    def first(self):
        """
        Returns the first value to try, which is the mean of the min_ and max_
        """
        self.last = (self.max_ + self.min_) / 2
        return round(self.last)

    def more(self):
        """
        If the last value was successful, shift the binary search interval to 
        be between last and max_, then return the new mean to try. 
        """
        self.min_ = self.last
        self.last = (self.max_ + self.min_) / 2
        return round(self.last)
    
    def less(self):
        """
        If the last value was not successful, shift the binary search interval to 
        be between min_ and last, then return the new mean to try. 
        """
        self.max_ = self.last
        self.last = (self.max_ + self.min_) / 2
        return round(self.last)
    
    def converged_initial(self):
        """
        If the difference between the max_ and min_ is less than 5, we are considered 
        to have converged and will then test values descending from max_
        """
        diff = self.max_ - self.min_
        if diff < 5:
            return True
        else:
            return False

def check_pass(runs, tolerance):
    """
    Checks if the percentage of failed runs is within the allowed tolerance. 
    """
    if percent_failed(runs) <= tolerance:
        return True
    else:
        return False

def n_failures(runs):
    """
    Returns the number of failed runs
    """
    runs = np.array(runs).astype(int)
    return len(runs) - sum(runs)

def percent_failed(runs):
    """
    Returns the percent of failed run
    """
    runs = np.array(runs).astype(int)
    return 1 - (sum(runs) / len(runs))

def suggest_n_tickets(expected_attendee_dist, seating: BaseSeating, bootstrap_samples, threshold=1.5,
                      tolerance=0.05, verbose=True):
    """
    A function that suggests a number of tickets to make available / a total number of attendees
    to allow. It does this by searching through the possible total numbers of attendees for a given 
    seating in a binary-search style. 

    Parameters
    ----------
    expected_attendee_dist : dict{int->float}
        a dict that maps group sizes to likelihood weights. The weights will be converted to
        probabilities and used to sample sets of attendees.
    seating: BaseSeating
        an empty Seating object to be filled
    bootstrap_samples: int
        the number of Attendees objects to sample and run. Larger samples will take longer but 
        produce more accurate suggestions. 
    threshold: float
        the social distancing target. Seatings that have pairs of individuals from different groups
        sitting closer together than threshold are considered in violation. 
    tolerance: float
        If the percentage of solved seatings that violates the threshold, for a given number of total 
        attendees, exceeds the tolerance, then this number of total attendees is considered too many, 
        and the search interval will shift to below the midpoint. 
    """
    # initialize searcher and get first n_attendees
    search = Search(0, seating.totalseats)
    n_attendees = search.first()

    # until "convergence", however convergence in this case is pseudo-convergence as we 
    # wait until the search interval is smaller than 5, and then search the remainder
    # exhaustively. 
    while not search.converged_initial():
        if verbose:
            print('searching, {} attendees'.format(n_attendees))
        if is_safe(expected_attendee_dist, copy.deepcopy(seating), n_attendees, bootstrap_samples, 
                   threshold, tolerance):
            # if this n_attendees is safe, shift search interval to look for more attendees
            n_attendees = search.more()
        else:
            # if this n_attendees is not safe, shift search interval to look for less attendees
            n_attendees = search.less()

    if verbose:
        print('initial convergence, search min = {}, search max = {}'.format(round(search.min_), round(search.max_)))

    # now that the search range is smaller, start from the max of the search range (rounding up)
    # and descend sequentially, returning the first successful n_attendees.  
    for proposed_n_attendees in range(int(search.max_) + 1, 0, -1):
        print('testing {} attendees'.format(proposed_n_attendees))
        if is_safe(expected_attendee_dist, copy.deepcopy(seating), proposed_n_attendees,
                   bootstrap_samples, threshold, tolerance):
            return proposed_n_attendees

def is_safe(expected_attendee_dist, seating, ticket_count, bootstrap_samples, threshold, tolerance, verbose=True, earlystop=25):
    """
    A function that determines whether a given number of tickets would be safe for a seating arrangement, 
    given an expected distribution of attendees, a social distancing threshold and a tolerane. 

    Parameters
    ----------
    expected_attendee_dist : dict{int->float}
        a dict that maps group sizes to likelihood weights. The weights will be converted to
        probabilities and used to sample sets of attendees.
    seating : BaseSeating
        an empty Seating object to be filled
    ticket_count : int
        the total number of tickets / number of attendees to allow
    bootstrap_samples : int
        the number of Attendees objects to sample and run. Larger samples will take longer but 
        produce more accurate safety predictions. 
    threshold : float
        the social distancing target. Seatings that have pairs of individuals from different groups
        sitting closer together than threshold are considered in violation. 
    tolerance : float
        If the percentage of solved seatings that violates the threshold exceeds the tolerance, 
        then this number of tickets is considered unsafe for this seating and the function returns False.
    earlystop : int
        If nonzero, after earlystop samples, if the percentage of threshold-violating samples is 
        already double the tolerance, the run stops early, returning False, and the setup is
        considered unsafe. 
    """
    
    def run_test():
        """
        Helper function to run an individual sample. 
        """
        # samples a new BaseAttendees from the weights in the expected_attendee_dist
        attendees = BaseAttendees.from_probs(expected_attendee_dist, ticket_count)
        test_seating = copy.deepcopy(seating)
        # solves the seating
        solver = ExhaustiveGreedySolver(test_seating, attendees)
        solver.solve()
        # evaluates whether the solved seating has no pairs of individuals from different
        # groups sitting closer together than the threshold
        good = evaluate_closerthan_thresh(test_seating, threshold, reduce_='boolean')
        return good
    
    runs = []
    # runs bootstrap_samples times
    for i in range(0, bootstrap_samples):
        good = run_test()
        if verbose and not good:
            print('run {} of {} failed'.format(i+1, bootstrap_samples))

        runs.append(good)

        # if earlystop != 0, and we have processed the earlystop amount of runs, and we fail
        # more than 2x what would be allowed according to the tolerance, the setup is considered
        # unsafe. 
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
