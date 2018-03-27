'''
Created on 15 Feb 2018

@author: danhbuithi
'''
import numpy as np

class NeighborBasedUnexpectedness(object):
    '''
    classdocs
    '''
    def __init__(self, delta1, delta2, delta3):
        '''
        Constructor
        '''
        self.delta1 = delta1
        self.delta2 = delta2
        self.delta3 = delta3
        
    def difference(self, itemset1, itemset2):
        x = set(itemset1).intersection(set(itemset2))
        return len(itemset1) + len(itemset2) - 2 * len(x)
    
    def distance(self, rule1, rule2):
        a = self.difference(rule1.get_itemset(), rule2.get_itemset())
        b = self.difference(rule1.left_items, rule2.left_items)
        c = self.difference(rule1.right_items, rule2.right_items)
        return self.delta1 * a + self.delta2 * b + self.delta3 * c
    
    '''
    Find unexpected rules from the list. 
    Each entry of the list is a rule and its confidence.
    r is the radius threshold for neighborhood. 
    '''
    def find_unexpectedness(self, association_rules, confidences, r, threshold):
        n_rules = len(association_rules)
        neighbors = np.zeros((n_rules, n_rules))
        
        for i in range(n_rules):
            for j in range(i+1, n_rules):
                x = self.distance(association_rules[i], association_rules[j])
                if x > r: continue
                neighbors[i,j] = 1
                neighbors[j,i] = 1
                
        all_conf = np.reshape(confidences, (1, -1))
        neighbors_count = np.sum(neighbors, axis = 0)
        
        means = np.dot(all_conf, neighbors)/neighbors_count
        stds = np.sqrt(np.sum(((all_conf - means.T) * neighbors)** 2, axis = 1)/(neighbors_count - 1)) 
        unexpectedness = np.abs(np.abs(all_conf - means) - stds)
        print(np.max(unexpectedness)) 
        return np.where(unexpectedness >= threshold) 
    