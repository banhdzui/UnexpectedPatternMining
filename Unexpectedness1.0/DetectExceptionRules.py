'''
Created on 02 Mar 2018

@author: danhbuithi
'''

import sys

from common.CommandArgs import CommandArgs

from rules_mining.RuleMiner import RuleMiner
from GenerateAssociationRules import min_conf
from rules_mining.AssociationRule import AssociationRule
from common.IOHelper import IOHelper



if __name__ == '__main__':
    config = CommandArgs({
                          'minsup'      : (0.01, 'Minimum support'),
                          'minconf'     : (0.8, 'Minimum confidence'),
                          'lowsup'      : (0.1, 'Low support threshold'),
                          'highsup'      : (0.2, 'High support threshold'),
                          'lowconf'      : (0.5, 'Low confidence threshold'),
                          'output'      : ('', 'Output file')
                          })
    
    if not config.load(sys.argv):
        print ('Argument is not correct. Please try again')
        sys.exit(2)
        
    miner = RuleMiner(None, None)
    association_rules_list = miner.load_association_rules()
    confidence_support_values = miner.compute_confidence(association_rules_list)
    
    freq_itemset_dict = miner.load_frequent_itemsets_as_dictionary()
    
    minsup = float(config.get_value('minsup'))
    minconf = float(config.get_value('minconf'))
    lowsup = float(config.get_value('lowsup'))
    highsup = float(config.get_value('highsup'))
    lowconf = float(config.get_value('lowconf'))
    
    
    exception_candidates = []
    strong_rules = []
    
    for i in range(len(association_rules_list)):
        conf = confidence_support_values[i][0]
        sup = confidence_support_values[i][1]/freq_itemset_dict.ntransactions
        
        if sup >= minsup and sup <= lowsup and conf >= minconf:
            exception_candidates.append(association_rules_list[i])
        elif sup > highsup and conf >= min_conf:
            strong_rules.append(association_rules_list[i])
            
    exception_rules = []
    for rule in strong_rules:
        for candidate in exception_candidates:
            if rule.right_items[0] == candidate.right_items[0]: continue
            if rule.is_satisfied(candidate.left_items) == False: continue
            B = set(candidate.left_items).difference(set(rule.left_items))
            reference_rule = AssociationRule(sorted(list(B)), candidate.right_items) 
            
            b_conf = freq_itemset_dict.get_confidence(reference_rule)
            b_sup = freq_itemset_dict.get_support(reference_rule)
            exception_rules.append((candidate.serialize(), b_conf, b_sup))
            
            
    IOHelper.save_as_json_format(config.get_value('output'), exception_rules)
            