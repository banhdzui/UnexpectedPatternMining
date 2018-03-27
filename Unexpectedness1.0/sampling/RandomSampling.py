'''
Created on Feb 28, 2017

@author: BanhDzui
'''

import random

class RandomSampling(object):
        
    @staticmethod
    def select_by_size(train_data_set, sample_size):
        n = min(train_data_set.size(), sample_size)
        return random.sample(train_data_set.train_data, n)
    
    
    @staticmethod
    def select_by_rate(input_file, sampling_rate, has_header = False):
        selected_data = []
        header = ''
        k = 0
        
        with open(input_file, "r") as text_file:
            if has_header == True:
                header = next(text_file)
            for line in text_file:
                r = random.uniform(0, 1)
                if r <= sampling_rate: 
                    selected_data.append(line.strip())
                    k += 1
                    if k % 5000 == 0: print('selected ' + str(k) + ' samples')
        return selected_data, header 