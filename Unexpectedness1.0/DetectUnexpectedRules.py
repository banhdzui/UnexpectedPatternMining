'''
Created on May 3, 2017

@author: BanhDzui
''' 

import sys
import os
import time

from common.IOHelper import IOHelper
from common.CommandArgs import CommandArgs
from common.ArgumentTuple import ContrastParams, dbscanParams

from rules_mining.RuleMiner import RuleMiner
from rules_mining.RulesClustering import UnexpectednessExtractor 
    
if __name__ == '__main__':
        
    config = CommandArgs({
                          'output'      : ('', 'Path of clusters file'),
                          'minpts'      : (3, 'Minimum of neighbors making a rule to become a core rule'),
                          'eps'         : (0.1, 'Radius of neighbors'),
                          'delta1'      : (0.0, 'Value of delta 1'),
                          'delta2'      : (-0.9, 'value of delta 2'),
                          'minconf'     : (0.8, 'Minimum confidence for unexpected rules'),
                          'subthres'    : (0.0, 'Threshold for substantial subset'),
                          'epsilon'     : (5e-3, 'Epsilon value')
                          })
    
    if not config.load(sys.argv):
        print ('Argument is not correct. Please try again')
        sys.exit(2)
    
    
    miner = RuleMiner(None, None)
    
    print('Loading features of association rules ....')
    X_train, lengths, lhs_feature_count, rhs_feature_count = miner.load_feature_vectors()
    association_rules_list = miner.load_association_rules()
    freq_itemset_dict = miner.load_frequent_itemsets_as_dict()
    
    delta1 = float(config.get_value('delta1'))
    delta2 = float(config.get_value('delta2'))
    minconf = float(config.get_value('minconf'))
    substantial_threshold = float(config.get_value('subthres'))
    epsilon = float(config.get_value('epsilon'))
    
    print('Threshold for substantial ' + str(substantial_threshold))
            
    contrast_params = ContrastParams(delta1, delta2,
                                      substantial_threshold, 
                                      lhs_feature_count, 
                                      rhs_feature_count)
    
    print ('Doing clustering ....')
    
    my_minpts = int(config.get_value('minpts'))
    my_eps = float(config.get_value('eps'))
    dbscan_params = dbscanParams(my_minpts, my_eps)
    
    output_name = config.get_value('output') + '.' + str(my_eps)
    clustering_engine = UnexpectednessExtractor(X_train, 
                                         freq_itemset_dict, 
                                         association_rules_list, 
                                         contrast_params,
                                         epsilon=epsilon,
                                         #reduced_rate=None)
                                         reduced_rate=0.5)
    start = time.time()
    cluster_labels = clustering_engine.run_dbscan(dbscan_params, nthreads = 4)
    end = time.time()
    print('execution time for clustering: ' + str(end - start))
    
    print('Computing confidences ....')
    rules_and_their_clusters = []
    confidence_support_values = miner.compute_confidence(association_rules_list)
    
    print('Saving clusters to the output file ....')
    for i in range(len(cluster_labels)):
        rule_key = association_rules_list[i].serialize()
        rules_and_their_clusters.append((rule_key, cluster_labels[i], 
                                         confidence_support_values[rule_key]))
        
    rules_and_their_clusters = sorted(rules_and_their_clusters, key=lambda x: x[1])
    
    os.makedirs(os.path.dirname(output_name), exist_ok=True)
    IOHelper.write_list_of_tuples(output_name, rules_and_their_clusters) 
    
    print('Finding unexpected patterns ....')
    unexpected_rules = clustering_engine.detect_unexpectedness(cluster_labels)
    IOHelper.save_as_json_format(output_name + '_' + str(delta1) + '.unexpected', unexpected_rules)
    