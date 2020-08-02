import numpy as np
import json
import types
import pickle
import copy


class BaseAttendees:
    """
    A class that represents all the people who have tickets to an event/flight/bus ride etc.
    The attendees are in groups, which represent attendees from the same household who can
    be seated together. 

    Attributes
    ----------
    groups : list[int]
        a list of ints that represent all the groups with tickets
        this list will shrink as seats are found for attendees
    init_groups : list[int]
        the initial groups before attendees were seated
    init_count : int
        the initial number of attendees with tickets
    generation_method : str
        the method with which these attendees were created

    Methods
    -------
    from_uniform(n_attendees, maximum)
        Class method which returns exactly n_attendees ticket holders sampled from a
        discrete uniform distribution over [1, maximum)
    
    from_decaying(n_attendees, lam, maximum)
        Class method which returns exactly n_attendees ticket holders sampled from a 
        distribution over [1, maximum) where the for each successive increase in group size,
        the probability of such a group being sampled decays by a factor of lam
    
    from_normal(n_attendees, mean, std, maximum)
        Class method which returns exactly n_attendees ticket holders sampled from a 
        discrete normal distribution over [1, maximum)

    from_custom(dict_)
        Class method which returns attendees as specified by a map - 
        {groupsize -> n_groups_of_this_size}

    from_probs(dict_, n_attendees)
        Class method which returns exactly n_attendees ticket holders, with the 
        probability of each group size being sampled coming from a map - 
        {groupsize -> relative_weight}
    
    from_json(name)
        Class method which returns an attendees object as specified in a json file
        which maps {groupsize -> n_groups_of_this_size}
    
    to_pickle(name)
        saves attendees in a pickle
    
    from_pickle(name)
        loads an attendees object from pickle
    
    def pop_largest()
        pops and returns the largest group that has not been seated
    
    def pop_smallest()
        pops and returns the smallest group that has not been seated
    
    def pop_random()
        pops and returns a random group that has not been seated

    def check_complete()
        checks if there are remaining groups to be seated
    """

    def __init__(self, groups, method):
        """
        Creates an BaseAttendees object

        groups : list[int]
            a list of ints that represent all the groups with tickets
            this list will shrink as seats are found for attendees
        method : str
            the method with which these attendees were created
        """
        groups.sort()
        self.groups = groups
        self.init_groups = copy.copy(groups)
        self.init_count = sum(groups)
        self.generation_method = method
    
    @classmethod
    def from_uniform(cls, n_attendees, maximum):
        """
        Returns attendees object w/ n_attendees ticket holders sampled from a
        discrete uniform distribution over [1, maximum)
        """

        groups = []

        # sample from uniform distribution until we pass n_attendees, then fill the 
        # remaining seats with a single group.
        new = np.random.randint(1, maximum)
        while new + sum(groups) < n_attendees:
            groups.append(new)
            new = np.random.randint(1, maximum)
        groups.append(n_attendees - sum(groups))
        return cls(groups, 'uniform')
        
    
    @classmethod
    def from_decaying(cls, n_attendees, lam, maximum):
        """
        returns exactly n_attendees ticket holders sampled from a 
        distribution over [1, maximum) where the for each successive increase in group size,
        the probability of such a group being sampled decays by a factor of lam
        """

        groups = []
        weights = [1]
        for i in range(1, maximum):
            weights.append(weights[i-1] * lam) # assign decaying probabilities
        
        # convert to probabilities
        tot = sum(weights)
        probabilities = [val / tot for val in weights]
        
        # convert to cumulative probabilities
        for i in range(1, len(probabilities)):
            probabilities[i] = probabilities[i] + probabilities[i-1]
        
        # sample using _get_weighted until we pass n_attendees, then fill remaining with a single group
        new = BaseAttendees._getweighted(probabilities)
        while new + sum(groups) < n_attendees:
            groups.append(new)
            new = BaseAttendees._getweighted(probabilities)
        groups.append(n_attendees - sum(groups))
        return cls(groups, 'decaying')
        

    @classmethod
    def from_normal(cls, n_attendees, mean, std, maximum):
        """
        Returns exactly n_attendees ticket holders sampled from a discrete normal(mean, std) distribution
        over [1, maximum)
        """
        
        # samples from a normla distribution
        def _getnormal(mean, std, maximum):
            sample = round(np.random.normal(mean, std))
            while sample < 1 or sample > maximum: # only take this sample if it is within the allowed bounds
                sample = round(np.random.normal(mean, std))
            return sample

        groups = []

        # sample using _get_normal until we pass n_attendees, then fill the remaining with a single group
        new = _getnormal(mean, std, maximum)
        while new + sum(groups) < n_attendees:
            groups.append(new)
            new = _getnormal(mean, std, maximum)
        groups.append(n_attendees - sum(groups))

        return cls(groups, 'normal')

    @classmethod
    def from_custom(cls, dict_):
        """
        returns attendees as specified by dict_, which maps {groupsize -> n_groups_of_this_size}
        """
        groups = []
        for key, value in dict_.items():
            groups.extend([key] * value)
        return cls(groups, 'custom')

    @classmethod
    def from_probs(cls, dict_, n_attendees):
        """
        returns exactly n_attendees ticket holders, with the weight that each group size is sampled 
        coming from dict_, which maps {groupsize -> relative_weight}
        """

        # Convert weights into probabilities by dividing by sum
        reweighted = {}
        sum_weights = sum(list(dict_.values()))
        for groupsize, weight in dict_.items():
            reweighted[groupsize] = weight / sum_weights

        # unpack and convert to cumulative probability        
        unpack_dict = [(key, value) for key, value in reweighted.items()]
        probabilities = [unpack_dict[0][1]]

        for i in range(1, len(unpack_dict)):
            probabilities.append(unpack_dict[i][1] + probabilities[i-1])
        

        # sample using _getweighted until we pass n_attendees, then fill remaining with single group
        groups = []
        new = BaseAttendees._getweighted(probabilities)
        while new + sum(groups) < n_attendees:
            groups.append(new)
            new = BaseAttendees._getweighted(probabilities)

        groups.append(n_attendees - sum(groups))
        return cls(groups, 'from_probs')
            
    @classmethod
    def _getweighted(cls, cumulative_probabilities):
        # samples from uniform, then finds which interval in cumulative_probabilities the 
        # sample corresponds to and returns the group size for that interval
        sample = np.random.uniform()
        for i in range(1, len(cumulative_probabilities) + 1): 
            # i does double duty here, as the index of the cum_prob and interval (group) to be returned
            if sample < cumulative_probabilities[i-1]:
                return i

    @classmethod
    def from_json(cls, name):
        """
        returns an attendees object as specified in a json file at saved/settings/[name]
        which maps {groupsize -> n_groups_of_this_size}
        """
        dict_ = json.load(open('saved/settings/{}'.format(name)))
        dict_ = {int(key): value for key, value in dict_.items()}
        return cls.from_custom(dict_)

    def to_pickle(self, name):
        """
        saves object to pickle at saved/objs/[name]
        """
        pickle.dump(open('saved/objs/{}'.format(name), 'wb'))

    def from_pickle(self, name):
        """
        loads object from pickle at saved/objs/[name]
        """
        return pickle.load(open('saved/objs/{}'.format(name), 'rb'))

    def pop_largest(self):
        """
        pops and returns the largest group that has not been seated
        """
        return self.groups.pop(-1)
    
    def pop_smallest(self):
        """
        pops and returns the smallest group that has not been seated
        """
        return self.groups.pop(0)

    def pop_random(self):
        """
        pops and returns a random group that has not been seated
        """
        return self.groups.pop(np.random.randint(0, len(self.groups)))

    def check_complete(self):
        """
        checks if there are groups left to be seated
        """
        if len(self.groups) == 0:
            return True
        else:
            return False

    

    
    

