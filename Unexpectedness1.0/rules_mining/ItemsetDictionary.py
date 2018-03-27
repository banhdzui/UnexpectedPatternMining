'''
Created on Apr 28, 2017

@author: BanhDzui
'''
from rules_mining.Helper import string_2_itemset

class ItemsetDictionary(object):
    

    def __init__(self, nTransaction = 0):
        self.itemsets = {}
        self.ntransactions = nTransaction
            
    def size(self):
        return len(self.itemsets)
    
    def exists(self, itemset_key):
        return itemset_key in self.itemsets
    
    def add_itemset(self, itemset_key, amount):
        self.itemsets[itemset_key] = amount
        
    def clear(self):
        self.itemsets.clear()
    
    def convert_2_indexes(self):
        k = 0
        dict_items_indexes = {}
        for item_name, _ in self.itemsets.items():
            dict_items_indexes[item_name] = k
            k += 1
        return dict_items_indexes
            
    def get_names(self):
        return self.itemsets.keys()
        
    def get_frequency(self, itemset_key):
        if self.exists(itemset_key):
            return self.itemsets[itemset_key]
        return 0
        
    def get_confidence(self, rule):
        left = self.get_frequency(rule.left_string())
        both = self.get_frequency(rule.itemset_string())
        if left == 0: return 0
        return both/left
    
    def get_frequency_tuple(self, rule):
        left = self.get_frequency(rule.left_string())
        right =self.get_frequency(rule.right_string())
        both = self.get_frequency(rule.itemset_string())
        
        return left, right, both
    
    def get_support(self, itemset_key):     
        return self.get_frequency(itemset_key)/self.ntransactions
       
    def split(self, nChunk):
        itemsets_names = self.itemsets.keys()
        nItemsets = len(itemsets_names)
        
        print ('Number of frequent item-sets: ' + str(nItemsets))
        itemset_chunks = [[] for _ in range(nChunk)]
        size_of_chunk = (int)(nItemsets/nChunk) + 1
                    
        index = 0
        counter = 0
        
        for itemset_key in itemsets_names:
            if counter < size_of_chunk:
                itemset_chunks[index].append(string_2_itemset(itemset_key))
                counter += 1
            elif counter == size_of_chunk:
                index += 1
                itemset_chunks[index].append(string_2_itemset(itemset_key))
                counter = 1  
                  
        return itemset_chunks
    
    def save_2_file(self, file_name, write_mode = 'a', write_support = False):
        with open(file_name, write_mode) as text_file:
            for key, value in self.itemsets.items():
                t = value
                if write_support == True:
                    t = value/self.ntransactions
                text_file.write(key + ':' + str(t))
                text_file.write('\n')
            
    def load_from_file(self,file_name):
        self.itemsets.clear()
        
        with open(file_name, "r") as text_file:
            self.ntransactions = int(text_file.readline())
            for line in text_file:
                #print (line)
                subStrings = line.split(':')
                itemset_key = subStrings[0].strip()
                frequency = int(subStrings[1].strip())
                
                self.itemsets[itemset_key] = frequency