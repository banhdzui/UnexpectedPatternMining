'''
Created on May 3, 2017

@author: BanhDzui
''' 

import sys
import numpy as np
import os
import time

from sklearn.metrics.pairwise import cosine_similarity

from common.IOHelper import IOHelper
from common.CommandArgs import CommandArgs

from rules_mining.RuleMiner import RuleMiner
from rules_mining.RulesClustering import ClusteringEngine 
from rules_mining.Helper import merge_itemsets, itemset_2_string
from rules_mining.AssociationRule import AssociationRule

def mark_unexpected_rules(features_of_beliefs, belief_rules,
                        features_of_noises, noises, 
                        freq_itemset_dict,
                        lhs_feature_count, unexpected_markers,
                        delta1 = 0.0, delta2 = -0.9):

    for i in range(len(noises)):
        right_noise_feature = np.reshape(features_of_noises[i,lhs_feature_count:], (1,-1))
        left_noise_feature = np.reshape(features_of_noises[i,:lhs_feature_count], (1, -1))
        
        left_similarities = cosine_similarity(left_noise_feature, 
                                              features_of_beliefs[:,:lhs_feature_count])
        right_similarities = cosine_similarity(right_noise_feature, 
                                               features_of_beliefs[:,lhs_feature_count:])
        potential_location = np.where(left_similarities > delta1)
        m = len(potential_location[0])
        for k in range(m):
            j = potential_location[1][k]
            if right_similarities[0][j] >= delta2:
                continue
            merged_itemset = merge_itemsets(noises[i].left_items, belief_rules[j].left_items)
            s = freq_itemset_dict.get_support(itemset_2_string(merged_itemset))
            if s == 0: continue
            c = freq_itemset_dict.get_confidence(belief_rules[j])
            unexpected_markers[i].append((belief_rules[j].serialize(), 
                             left_similarities[0][j], 
                             right_similarities[0][j], s, c))

def load_rules_and_their_clusters(input_file):
    rules_and_their_clusters = []
    with open(input_file, 'r') as file_reader:
        for line in file_reader:
            sub_strings = line.split('\'')
            rule_text = sub_strings[1].strip('(\' ')
            temp = sub_strings[2].split(',')
            
            cluster_id = int(temp[1])
            rules_and_their_clusters.append((rule_text, cluster_id))
            
    return rules_and_their_clusters
    
if __name__ == '__main__':
        
    config = CommandArgs({
                          'output'      : ('', 'Path of clusters file'),
                          'minpts'      : (3, 'Minimum of neighbors making a rule to become a core rule'),
                          'eps'         : (0.1, 'Radius of neighbors'),
                          'delta1'      : (0.0, 'Value of delta 1'),
                          'delta2'      : (-0.9, 'value of delta 2')
                          })
    
    if not config.load(sys.argv):
        print ('Argument is not correct. Please try again')
        sys.exit(2)
    
    
    miner = RuleMiner(None, None)
    
    print('Loading features of association rules ....')
    X_train, lengths, _, _ = miner.load_feature_vectors()
    
    print ('Doing clustering ....')
    my_eps = float(config.get_value('eps'))
    my_minpts = int(config.get_value('minpts'))
    
    clustering_engine = ClusteringEngine(X_train.todense())
    start = time.time()
    _, cluster_labels = clustering_engine.run_dbscan(my_eps, my_minpts, 4)
    end = time.time()
    clustering_engine = None
    print('execution time for clustering: ' + str(end - start))
    
    print('Computing confidences ....')
    rules_and_their_clusters = []
    association_rules_list = miner.load_association_rules()
    confidence_support_values = miner.compute_confidence(association_rules_list)
    
    print('Saving clusters to the output file ....')
    for i in range(len(cluster_labels)):
        rule_key = association_rules_list[i].serialize()
        rules_and_their_clusters.append((rule_key, cluster_labels[i], 
                                         confidence_support_values[rule_key])
                                        )
        
    rules_and_their_clusters = sorted(rules_and_their_clusters, key=lambda x: x[1])
    
    os.makedirs(os.path.dirname(config.get_value('output')), exist_ok=True)
    IOHelper.write_list_of_tuples(config.get_value('output'), rules_and_their_clusters) 
    
    X_train = None
    association_rules_list = None
    rules_and_their_clusters = None
    confidence_support_values = None

    print('Finding unexpected patterns ....')
    rules_and_their_clusters = load_rules_and_their_clusters(config.get_value('output'))
    rules_and_their_features, lhs_feature_count, _ = miner.load_rules_and_their_features()
    
    print('Loading noises from clustering....')
    features_of_noises = []
    noises = []
    for rule_text, cluster_id in rules_and_their_clusters:
        if cluster_id == -1:
            features_of_noises.append(rules_and_their_features[rule_text])
            noises.append(AssociationRule.string_2_rule(rule_text))
        else:
            break
        
    unexpected_markers ={i : [] for i in range(len(noises))}
    print ('Number of noise rules: ' + str(len(noises)))
    features_of_noises = np.array(features_of_noises)
    
    print('Comparing noises with beliefs....')
    delta1 = float(config.get_value('delta1'))
    delta2 = float(config.get_value('delta2'))
    
    i = 0
    beliefs = []   
    features_of_beliefs = []
    freq_itemset_dict = miner.load_frequent_itemsets_as_dictionary()
    for rule_text, cluster_id in rules_and_their_clusters:
        if cluster_id < i: continue
        if cluster_id > i: 
            print('cluster----' + str(i))
            mark_unexpected_rules(np.array(features_of_beliefs), 
                                  beliefs, 
                                  features_of_noises,
                                  noises,
                                  freq_itemset_dict, 
                                  lhs_feature_count, 
                                  unexpected_markers,
                                  delta1, delta2)
            
            features_of_beliefs.clear()
            beliefs.clear()
            
            i += 1
        features_of_beliefs.append(rules_and_their_features[rule_text])
        beliefs.append(AssociationRule.string_2_rule(rule_text))
    
    mark_unexpected_rules(np.array(features_of_beliefs), 
                          beliefs,
                          features_of_noises,
                          noises,
                          freq_itemset_dict,
                          lhs_feature_count, 
                          unexpected_markers,
                          delta1, delta2)
    
    features_of_beliefs.clear()
    beliefs.clear()
          
    print('Saving unexpected rules to the output file ....')  
    rules_and_their_clusters = None
    unexpected_rules = []
    for key, value in unexpected_markers.items():
        if len(value) == 0:
            continue
        c = freq_itemset_dict.get_confidence(noises[key])
        sorted_value = sorted(value, key=lambda x: x[1], reverse=True)
        del sorted_value[3: ]
        unexpected_rules.append((noises[key].serialize(), c, sorted_value))
        
    unexpected_rules = sorted(unexpected_rules, key=lambda x: x[2][0][1], reverse=True)
    #unexpected_rules = sorted(unexpected_rules, key=lambda x: x[1], reverse=True)
    print ('number of unexpectedness: ' + str(len(unexpected_rules)))
    IOHelper.save_as_json_format(config.get_value('output') + '.unexpected', unexpected_rules)
    