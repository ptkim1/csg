import numpy as np
import json
from dotted_dict import DottedDict
import types
import pickle
import copy


class BaseAttendees:

    def __init__(self, groups, distribution):
        groups.sort()
        self.groups = groups
        self.init_groups = groups
        self.init_count = sum(groups)
        self.generating_distribution = distribution
    
    @classmethod
    def from_uniform(cls, n_attendees, maximum):
        groups = []
        # select from uniform distribution until we pass n_attendees, then fill the rest with the remaining seats
        new = np.random.randint(1, maximum)
        while new + sum(groups) < n_attendees:
            groups.append(new)
            new = np.random.randint(1, maximum)
        groups.append(n_attendees - sum(groups))
        return cls(groups, 'uniform')
        
    
    @classmethod
    def from_decaying(cls, n_attendees, lam, maximum):

        def _getweighted(cumulative_probabilities):
            sample = np.random.uniform()
            for i in range(1, len(cumulative_probabilities) + 1):
                if sample < cumulative_probabilities[i-1]:
                    return i

        groups = []
        probabilities = [1]
        for i in range(1, maximum):
            probabilities.append(probabilities[i-1] * lam)
        
        # convert to probabilities
        tot = sum(probabilities)
        probabilities = [val / tot for val in probabilities]
        
        # figure out some kind of dice based on the probabilities
        for i in range(1, len(probabilities)):
            probabilities[i] = probabilities[i] + probabilities[i-1]
        
        new = _getweighted(probabilities)
        while new + sum(groups) < n_attendees:
            groups.append(new)
            new = _getweighted(probabilities)
        groups.append(n_attendees - sum(groups))
        return cls(groups, 'decaying')
        
        # generate groups from poisson

    @classmethod
    def from_normal(cls, n_attendees, mean, std, maximum):
        
        def _getnormal(mean, std, maximum):
            sample = round(np.random.normal(mean, std))
            while sample < 1 or sample > maximum:
                sample = round(np.random.normal(mean, std))
            return sample
        groups = []

        new = _getnormal(mean, std, maximum)
        while new + sum(groups) < n_attendees:
            groups.append(new)
            new = _getnormal(mean, std, maximum)
        groups.append(n_attendees - sum(groups))

        return cls(groups, 'normal')

    @classmethod
    def from_custom(cls, dict_):
        # from a dict defining custom groups
        groups = []
        for key, value in dict_.items():
            groups.extend([key] * value)
        return cls(groups, 'custom')

    @classmethod
    def from_json(cls, name):
        dict_ = json.load(open('saved/settings/{}'.format(name)))
        dict_ = {int(key): value for key, value in dict_.items()}
        return cls.from_custom(dict_)

    def to_pickle(self, name):
        pickle.dump(open('saved/objs/{}'.format(name), 'wb'))

    def from_pickle(self, name):
        return pickle.load(open('saved/objs/{}'.format(name), 'rb'))

    def pop_largest(self):
        return self.groups.pop(-1)
    
    def pop_smallest(self):
        return self.groups.pop(0)

    def iter_ascending(self):
        return (p for p in self.groups)
    
    def iter_descending(self):
        groups_descending = copy.copy(self.groups)
        groups_descending.sort(reverse=True)
        return (p for p in groups_descending)

    
    

