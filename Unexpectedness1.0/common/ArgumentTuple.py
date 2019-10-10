'''
Created on 25 Sep 2018

@author: danhbuithi
'''

class ContrastParams(object):
    '''
    classdocs
    '''

    def __init__(self, delta1, delta2, share_threshold, n_lhs_features, n_rhs_features):
        '''
        Constructor
        '''
        self.delta1 = delta1 
        self.delta2 = delta2 
    
        self.share_threshold = share_threshold
        self.n_lhs_features = n_lhs_features
        self.n_rhs_features = n_rhs_features
        
class ARMParams(object):
    '''
    classdocs
    '''

    def __init__(self, minsup, minconf, itemset_max_size=-1):
        '''
        Constructor
        '''
        self.min_sup = minsup 
        self.min_conf = minconf
        self.itemset_max_size = itemset_max_size
        
class dbscanParams(object):
    
    def __init__(self, minpts, eps):
        self.min_pts = minpts
        self.eps = eps
        
class ARMFiles(object):
    '''
    classdocs
    '''

    def __init__(self, default_folder = 'tmp/'):
        '''
        Constructor
        '''
        self.temp_folder = default_folder
        
        self.itemset_tmp_file = self.temp_folder + 'miner.tmp.itemsets'
        self.rules_tmp_file = self.temp_folder + 'miner.tmp.rules'
        self.best_rules_file = self.temp_folder + 'miner.best_tmp.rules'
        
        self.interestingness_tmp_file = self.temp_folder +'miner.tmp.interestingness'
        self.probabilities_tmp_file = self.temp_folder +'miner.tmp.probabilities'
        
        self.feature_tmp_file = self.temp_folder +'miner.tmp.features'
        self.non_redundant_rule_tmp_file = self.temp_folder +'miner.tmp.non_redundant_rules'
        self.non_redundant_rule_feature_tmp_file = self.temp_folder + 'miner.tmp.non_redundant_rules.features'
        self.relation_tmp_file = self.temp_folder + 'relation_matrix.csv'
        
    def get_rule_file(self, i):
        return self.rules_tmp_file + '.' + str(i)
    