'''
Created on Apr 14, 2017

@author: BanhDzui
'''
from rules_mining.Helper import merge_itemsets, itemset_2_string, string_2_itemset
import math
import json
import numpy as np
from scipy.stats import stats

class InformationGain(object):
    
    def __init__(self, freq_itemset_dict, class_dict, itemset_formatter):
        self.freq_itemset_dict = freq_itemset_dict
        self.class_dict = class_dict
        self.itemset_formatter = itemset_formatter
        
    def lookup_frequency(self, item_set, class_name):
        merge_itemset = merge_itemsets(item_set, [class_name])
        merge_itemset_key = itemset_2_string(merge_itemset)
        if self.freq_itemset_dict.exists(merge_itemset_key):
            return self.freq_itemset_dict.get_frequency(merge_itemset_key)
        return 0
            
        
    def generate_rules_for_class(self, general_summary, class_name):
        special_summary = []
        for summary_detail in general_summary:
            if summary_detail[1][class_name] > 0:
                special_summary.append(summary_detail)
                '''
                Compute p-value
                '''
                item_set = string_2_itemset(summary_detail[0])
                satisfy_rule = self.freq_itemset_dict.get_frequency(summary_detail[0])
                no_satisfy_rule = self.freq_itemset_dict.ntransactions - satisfy_rule
                
                correct_predict = self.lookup_frequency(item_set, class_name)
                incorrect_predict = satisfy_rule - correct_predict
                
                belong_to_class = self.freq_itemset_dict.get_frequency(class_name)
                no_rule_belong_to_class = belong_to_class - correct_predict
                contingency_matrix = np.array([[correct_predict, incorrect_predict],
                                               [no_rule_belong_to_class, no_satisfy_rule - no_rule_belong_to_class]]) 
                
                _, p_value = stats.fisher_exact(contingency_matrix)
                summary_detail[1]['p-value'] = p_value
                
        return special_summary
    
    def generate_network(self, special_summary, class_name):
        item_pairs_and_frequency = {}
        for summary_detail in special_summary:
            if (summary_detail[1]['p-value']) <= 0.05:
                item_set = string_2_itemset(summary_detail[0])
                for i in range(len(item_set) - 1):
                    for j in range(i + 1, len(item_set)):
                        combination = [item_set[i], item_set[j]]
                        combination_key = itemset_2_string(combination)
                        if combination_key in item_pairs_and_frequency: continue
                        item_pairs_and_frequency[combination_key] = self.lookup_frequency(combination, class_name)
        
        return item_pairs_and_frequency
        
        '''
        This code only use for ANK3 dataset.
        gene_pairs_and_frequency = {}
        for k, v in item_pairs_and_frequency.items():
            item_set = string_2_itemset(k)
            gene01 = item_set[0].split('@')[0]
            gene02 = item_set[1].split('@')[0]
            
            gene_pair_key = itemset_2_string([gene01, gene02])
            if gene_pair_key not in gene_pairs_and_frequency:
                gene_pairs_and_frequency[gene_pair_key] = 0
            gene_pairs_and_frequency[gene_pair_key] += v
            
        return gene_pairs_and_frequency
        '''
    
    
    def save_network(self, network, output_file):
        with open(output_file, 'w') as text_writer:
            for k, v in network.items():
                text_writer.write(k + ',' + str(v))
                text_writer.write('\n')
            
                        
    def compute(self):
        statistic_summary = []
        
        class_list = self.class_dict.keys()
        for itemset_key, freq in self.freq_itemset_dict.itemsets.items():
            '''
            Compute entropy for each item-set (not contain class item)
            '''
            itemset = string_2_itemset(itemset_key)
            if self.itemset_formatter(itemset) == True: continue
            
            entropy_value = 0
            statistic_detail = {}
            flag = False
            
            for class_name in class_list:
                p = self.lookup_frequency(itemset, class_name)/freq
                statistic_detail[class_name] =  p
                if p != 0:
                    flag = True
                    entropy_value += (-p * math.log2(p))
                
            '''
            Only add value when at least one class has value.
            '''
            if (flag == True):    
                statistic_detail['entropy'] = entropy_value
                statistic_detail['freq'] = freq
                
                statistic_summary.append((itemset_2_string(itemset), statistic_detail))
                    
        return sorted(statistic_summary, key = lambda x: (x[1]['entropy']))
      
    
    def save(self, statistic_summary, output_file_name):
        with open(output_file_name, 'w') as output_file:
            for statistic_detail in statistic_summary:
                output_file.write(json.dumps(statistic_detail))
                output_file.write('\n')
                    
            
            
        