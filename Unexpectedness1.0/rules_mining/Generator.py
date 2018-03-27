from rules_mining.AssociationRule import AssociationRule
from rules_mining.Helper import itemset_2_string

from multiprocessing import Process
import json
from rules_mining.RulesCollection import RulesCollection

class Generator:
    
    def __init__(self, freq_itemset_dict, 
                 min_conf, 
                 itemset_formatter, 
                 rule_formatter, 
                 nThreads):
        self.itemset_formatter = itemset_formatter
        self.rule_formatter = rule_formatter
        
        self.nthreads = nThreads
        self.freq_itemset_dict = freq_itemset_dict
        
        self.min_conf = min_conf
    
    @staticmethod
    def string_2_rule_and_support(s):
        subStrings = s.split('#')
        rule  = Generator.string_2_rule(subStrings[0].strip())
        v = json.loads(subStrings[1].strip())
        return rule, v
    
    @staticmethod
    def rule_and_support_2_string(rule, p):
        return rule.serialize() + '#' + json.dumps(p)
                
    '''
    Generate association rules for one item-set
    '''
    def subsets(self, bits, item_set, k, rule_collection, total_freq): 
        '''
        Run out of items --> create rule and check format criterion
        '''
        if k >= len(item_set):
            left = []
            right = []
                    
            for index in range(len(bits)):
                if bits[index] == True:
                    left.append(item_set[index])
                else:
                    right.append(item_set[index])
                                      
            if (len(left) > 0 and len(right) > 0):
                rule = AssociationRule(left, right)
                if (self.rule_formatter == None or self.rule_formatter(rule) == True):
                    rule_collection.add(rule)
            
            return 
      
        value_domain = [True, False]
        '''
        Include k-th item into LHS 
        '''
        
        for value in value_domain:
            bits[k] = value
               
            if (value == False):
                left_itemset = []
                for index in range(len(bits)):
                    if bits[index] == True:
                        left_itemset.append(item_set[index])
                        
                left_value = self.freq_itemset_dict.get_frequency(itemset_2_string(left_itemset))
                confident = 0
                if left_value > 0: confident = total_freq/left_value
                
                if confident < self.min_conf:
                    bits[k] = True
                    continue
                self.subsets(bits, item_set, k+1, rule_collection, total_freq)
            else:
                self.subsets(bits, item_set, k+1, rule_collection, total_freq)
                
            bits[k] = True
    '''
    Generate association rules for a set of item-sets and write results to a file
    '''
    def generate_rules(self, freq_itemsets_collection, output_file_name):
        total_rules = 0
        remaining_rules = 0
        k = 0
        rule_collection = RulesCollection()
        with open(output_file_name, 'w') as _:
            print ('clear old file...')
            
        for itemset in freq_itemsets_collection:
            '''
            Check item-set first if it can generate a rule
            '''
            if len(itemset) == 1:
                continue
     
         
            if self.itemset_formatter is not None and \
            self.itemset_formatter(itemset) == False:
                continue
            
            '''
            Write generated rule_collection into file
            '''
            k += 1
            if k % 200 == 0:
                print ('writing some rule_collection to file: ' + str(k))
                total_rules += rule_collection.size()
                rule_collection.remove_redundancy(self.freq_itemset_dict)
                rule_collection.save(output_file_name, True)
                remaining_rules += rule_collection.size()
                rule_collection.clear()
            
            '''
            Generating association rule_collection.
            '''
            total_freq = self.freq_itemset_dict.get_frequency(itemset_2_string(itemset))
            bits = [True] * len(itemset)
            self.subsets(bits, itemset, 0, rule_collection, total_freq)
                    
        print ('writing last rule_collection to file: ' + str(k))
        total_rules += rule_collection.size()
        rule_collection.remove_redundancy(self.freq_itemset_dict)
        rule_collection.save(output_file_name, True)
        remaining_rules += rule_collection.size()
        rule_collection.clear()
        
        print ('Finish for sub frequent item-sets!!!')
        print ('Number of redundant rules ' + str(total_rules - remaining_rules) + '/' + str(total_rules))
                  
    '''
    Generate association rules for whole data-set
    '''  
    def execute(self, output_file_name):
        
        itemset_chunks = self.freq_itemset_dict.split(self.nthreads)
        
        processes = []
        for index in range(self.nthreads):
            file_name = output_file_name + '.' + str(index)
            process_i = Process(target=self.generate_rules, 
                                args=(itemset_chunks[index], file_name))
            processes.append(process_i)
            
            
        for process_i in processes:
            process_i.start()
            
        # wait for all thread completes
        for process_i in processes:
            process_i.join()
            
        print ('Finish generating rules!!!!')    
            
            