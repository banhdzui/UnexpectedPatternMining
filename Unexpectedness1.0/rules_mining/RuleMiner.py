'''
Created on Apr 6, 2017

@author: BanhDzui
'''
from rules_mining.Apriori import Apriori
from rules_mining.Generator import Generator
from rules_mining.ItemsetDictionary import ItemsetDictionary

from rules_mining.ItemsetFormatter import ItemsetFormatter
from rules_mining.RuleFormatter import RuleFormatter
from rules_mining.AssociationRule import AssociationRule

from objective_measures.Interestingness import ObjectiveMeasure as om
from rules_mining.RulesCollection import RulesDictionary

import json
from scipy import sparse
import numpy as np

class RuleMiner(object):    
    '''
    This class is used to generate_itemsets_and_rules and store a Naive Belief System 
    by using the most confident association rules
    '''

    def __init__(self, filter_name, train_data_set):
        
        self.temp_folder = 'tmp/'
        
        self.itemset_tmp_file = self.temp_folder + 'miner.tmp.itemsets'
        self.rules_tmp_file = self.temp_folder + 'miner.tmp.rules'
        self.best_rules_file = self.temp_folder + 'miner.best_tmp.rules'
        
        self.interestingness_tmp_file = self.temp_folder +'miner.tmp.interestingness'
        self.probabilities_tmp_file = self.temp_folder +'miner.tmp.probabilities'
        
        self.filter_name = filter_name
        self.data_set = train_data_set
        
        self.nthreads = 4
    
        self.relation_matrix = None 
        
        self.feature_tmp_file = self.temp_folder +'miner.tmp.features'
        self.non_redundant_rule_tmp_file = self.temp_folder +'miner.tmp.non_redundant_rules'
        self.non_redundant_rule_feature_tmp_file = self.temp_folder + 'miner.tmp.non_redundant_rules.features'
        self.relation_tmp_file = self.temp_folder + 'relation_matrix.csv'
        
        if self.data_set is not None:
            self.relation_matrix = self.data_set.items_relationship()
            #print(self.relation_matrix.item_dict)
        
    '''
    Load generated frequent itemsets from file. 
    This method must be called after generate_frequent_itemsets is called
    '''
    def load_frequent_itemsets_as_dictionary(self):
        freq_itemset_dict = ItemsetDictionary(0)
        freq_itemset_dict.load_from_file(self.itemset_tmp_file)
        return freq_itemset_dict
    
    '''
    Load generated association rules from file. 
    This method must be called after generate_association_rules is called
    '''
    def load_rules_as_dictionary(self):
        rules_dict = RulesDictionary()
        
        for i in range(self.nthreads):
            file_name = self.rules_tmp_file + '.' + str(i)
            rules_dict.load_from_file(file_name)
                
        return rules_dict

        
    '''
    Generate frequent itemsets from data-set
    '''
    def generate_frequent_itemsets(self, min_sup, itemset_max_size):
        
        print ('generating frequent item-sets...')
        apriori = Apriori(self.data_set)
        apriori.generate_frequent_itemsets_vw(min_sup * self.data_set.size(), 
                                              self.nthreads, 
                                              itemset_max_size, 
                                              self.itemset_tmp_file)
        
    '''
    Generate association rules from data-set. 
    This method must be called after generate_frequent_itemsets(...) is called
    '''
    def generate_association_rules(self, min_conf):
        freq_itemsets_dict = self.load_frequent_itemsets_as_dictionary()
        
        print ('generating rules ....')
        itemset_formatter = getattr(ItemsetFormatter, self.filter_name)
        rule_formatter = getattr(RuleFormatter, self.filter_name)
        rule_generator = Generator(freq_itemsets_dict, 
                                   min_conf, 
                                   itemset_formatter, 
                                   rule_formatter, 
                                   self.nthreads)
        rule_generator.execute(self.rules_tmp_file)
        
    '''
    Generate association rules and select K patterns with highest confidence.
    '''    
    def generate_itemsets_and_rules(self, min_sup, min_conf, itemset_max_size = -1):
        self.generate_frequent_itemsets(min_sup, itemset_max_size)
        self.generate_association_rules(min_conf)
        self.extract_feature_vectors_()
         
    '''
    Compute confidence for all association rules generated from data-set
    '''
    def compute_confidence(self, association_rules_list):
        freq_itemset_dict = self.load_frequent_itemsets_as_dictionary()
        
        rule_confidence_dict = {}
        for rule in association_rules_list:
            left, _, both = freq_itemset_dict.get_frequency_tuple(rule)
            rule_confidence_dict[rule.serialize()] = (both/left, both)
        return rule_confidence_dict

    '''
    Compute values of 31 interestingness measures for all association rules generated from data-set
    '''
    def compute_interestingnesses(self, output_file):
        print ('computing correlation among interestingness measures...')
        #measures = [om.confidence, om.lift]
        
        measures = [om.confidence, om.coverage, om.prevalence, om.recall, om.specificity, 
                    om.accuracy, om.lift, om.leverage, om.change_of_support, om.relative_risk, 
                    om.jaccard, om.certainty_factor, om.odd_ratio, om.yuleQ, om.yuleY, 
                    om.klosgen, om.conviction, om.weighting_dependancy, 
                    om.collective_strength, om.laplace_correction, om.jmeasure, 
                    om.one_way_support, om.two_way_support, om.two_ways_support_variation, 
                    om.linear_correlation_coefficient, om.piatetsky_shapiro, om.loevinger,
                    om.information_gain, om.sebag_schoenauner, om.least_contradiction, 
                    om.odd_multiplier, om.counter_example_rate, om.zhang]
        
        print('loading frequent item-sets....')
        freq_itemsets_dict =  self.load_frequent_itemsets_as_dictionary()
        association_rules = self.load_association_rules()
        
        print ('computing interestingness for all rules ....')
        
        with open(output_file, 'w') as write_file:
            total = freq_itemsets_dict.ntransactions
            for rule in association_rules:
                left, right, both = freq_itemsets_dict.get_frequency_tuple(rule)
                interestingness = []
                for index in range(len(measures)):
                    value = measures[index](left, right, both, total)
                    interestingness.append(value)
                write_file.write(rule.serialize() + ';')            
                write_file.write(';'.join([str(x) for x in interestingness]))
                write_file.write('\n')
                
    '''
    Determine collection of features for LHS and RHS of rules.
    This method returns two dictionaries for LHS and RHS respectively. 
    Each entry of the dictionaries are (the name of item : its index in feature vector)
    ''' 
    def get_features_(self):
        
        left_features = []
        right_features = []
        
        left_filter = getattr(RuleFormatter, self.filter_name + 'Left')
        right_filter = getattr(RuleFormatter, self.filter_name + 'Right')        
        for item in self.relation_matrix.get_items():
            if left_filter(item):
                left_features.append(item)
            if right_filter(item):
                right_features.append(item) 
                    
        return sorted(left_features), sorted(right_features)
    
    '''
    Extract feature for an item-set.
    '''
    def extract_features_(self, itemset, feature_names):
        n = len(feature_names)
        f_vector = [0 for _ in range(n)]
        for item in itemset:
            for i in range(n):
                a = self.relation_matrix.get_value(item, feature_names[i])
                if (abs(f_vector[i]) < abs(a)):
                    f_vector[i] = a
        return np.array(f_vector) 
    '''
    Extract feature vectors for all rules 
    '''
    def extract_feature_vectors_(self):
        left_features, right_features  = self.get_features_()
        left_count = len(left_features)
        right_count = len(right_features)
        
        print('Write number of features for LHS and RHS')
        features_writer = open(self.non_redundant_rule_tmp_file, 'w')
        features_writer.write(str(left_count))
        features_writer.write('\n')
        features_writer.write(str(right_count))
        features_writer.write('\n')
        
        print('Starting extraction...')
        for i in range(self.nthreads):
            input_file = self.rules_tmp_file + '.' + str(i)
            
            with open(input_file, 'r') as rules_reader:
                for line in rules_reader:
                    rule = AssociationRule.string_2_rule(line.strip())
                    a = self.extract_features_(rule.left_items, left_features)
                    b = self.extract_features_(rule.right_items, right_features)
                    f_vector = np.concatenate((a, b))
                    '''
                    Write a feature vector to file
                    '''               
                    features_writer.write(json.dumps((rule.serialize(),f_vector.tolist())))
                    features_writer.write('\n')
        features_writer.close()
        
    '''
    Load feature vectors for all non-redundant rules
    '''
    def load_feature_vectors(self):
        rows = []
        columns = []
        data = []
        
        nRows = 0
        nColumns = 0
        lengths = []
        
        with open(self.non_redundant_rule_tmp_file, 'r') as feature_reader:
            print('Loading number of LHS and RHS features...')
            lhs_count = int(feature_reader.readline())
            rhs_count = int(feature_reader.readline())
            print('Loading feature vectors... ')
            for line in feature_reader:
                rule_text, f_vector = json.loads(line.strip())
                rule = AssociationRule.string_2_rule(rule_text.strip())
                lengths.append(rule.length())
                rule = None
                
                nColumns = len(f_vector)
                for i in range(nColumns):
                    if f_vector[i] != 0:
                        rows.append(nRows)
                        columns.append(i)
                        data.append(f_vector[i])
                nRows += 1
                
        return sparse.csr_matrix((data, (rows, columns)), shape=(nRows, nColumns)), lengths, lhs_count, rhs_count
        
    '''
    Load non-redundant rules from a file.
    '''
    def load_association_rules(self):
        association_rules_list = []
        with open(self.non_redundant_rule_tmp_file, 'r') as rules_reader:
            rules_reader.readline()
            rules_reader.readline()
            
            for line in rules_reader:
                rule_text, _ = json.loads(line.strip())
                association_rules_list.append(AssociationRule.string_2_rule(rule_text.strip()))
        return association_rules_list
        
    '''
    Load non-redundant rules and their feature vectors from a file
    '''
    def load_rules_and_their_features(self):
        rules_and_their_features = {}
        with open(self.non_redundant_rule_tmp_file, 'r') as feature_reader:
            lhs_count = int(feature_reader.readline())
            rhs_count = int(feature_reader.readline())
            
            for line in feature_reader:
                rule_text, f_vector = json.loads(line.strip())
                rules_and_their_features[rule_text] = f_vector
        return rules_and_their_features, lhs_count, rhs_count
        
    