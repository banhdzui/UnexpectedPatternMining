'''
Created on 16 Feb 2018

@author: danhbuithi
'''

class DictionaryHelper:
    
    @staticmethod
    def revert_key_value(my_dict):
        return {v : k for k, v in my_dict.items()}
    
    
    @staticmethod 
    def group_indices_by_value(arr):
        index_dict = {}
        for i in range(len(arr)):
            if arr[i] not in index_dict:
                index_dict[arr[i]] = []
            index_dict[arr[i]].append(i)
        return index_dict