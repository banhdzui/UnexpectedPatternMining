from multiprocessing import Process
from multiprocessing.managers import BaseManager

from rules_mining.HashTable import HashTable
from rules_mining.HashItem import HashItem
from rules_mining.HashItemCollection import HashItemCollection

import numpy as np

class Apriori:
    def __init__(self, train_data_set):
        self.tmp_folder = 'tmp/'
        self.freq_itemsets_tmp_file = self.tmp_folder + 'freqitemsets.tmp'
        self.itemsets_tmp_file = self.tmp_folder + 'itemsetscandidates.tmp'
        self.freq_k_item_sets_tmp_file = self.tmp_folder + 'freq_k_itemsets.tmp'
        self.data_set = train_data_set
        self.L1 = None
        
    
    def generate_L1(self, min_sup):
        C_1 = HashTable()
        itemset_key = ''
        C_1.insert_key(itemset_key)
    
        n = self.data_set.size()
        print ('size of data-set: ' + str(n))
        
        for tid in range(n):
            transaction = self.data_set.get_transaction(tid)
            for item in transaction:
                C_1.add_tid(itemset_key, item, tid)
            
        print ('get frequent item sets with 1 item')
        self.L1 = C_1.generate_frequent_itemsets(min_sup)
      
    @staticmethod
    def generate_Lk(min_sup, L_k1, C_k, k):
        print('generate candidates with ' + str(k) + ' items')
        for key, hash_item_collection in L_k1.get_items():
            for index in range(hash_item_collection.size() - 1):
                
                index_th_item = hash_item_collection.get_item(index)
                new_key = ''
                if key == '':
                    new_key = index_th_item.last_item
                else:
                    new_key = key +',' + index_th_item.last_item
                new_hash_collection = HashItemCollection()
                
                #check if it is infrequent item-set
                for item in hash_item_collection.get_items_from(index + 1):
                    new_item = HashItem(item.last_item)
                    inter_items = set(index_th_item.tids).intersection(item.tids)      
                    if len(inter_items) >= min_sup:  
                        new_item.add_tids(list(inter_items))
                        new_hash_collection.add_item(new_item)
                        
                if new_hash_collection.size() > 0:        
                    C_k.insert(new_key,  new_hash_collection) 

    def generate_frequent_itemsets(self, min_sup, nthreads, end, output_file, write_support = False):
        
        '''
        Step 1: Generate frequent item-sets with 1 item and write to file
        '''
        nTransactions = self.data_set.size()
        with open(output_file, 'w') as text_file:
            text_file.write(str(nTransactions))
            text_file.write('\n')
        
        
        self.generate_L1(min_sup)
        freq_itemsets_dict = self.L1.generate_itemset_dictionary()
        freq_itemsets_dict.ntransactions = nTransactions
        freq_itemsets_dict.save_2_file(output_file, 'a', write_support)
        freq_itemsets_dict.clear()
        
        '''
        Step 2: Generate frequent item-sets with more than 1 item and append to the file
        '''
        k = 2    
        L_k1 = self.L1
        
        while not L_k1.is_empty() and (end == -1 or k <= end):
            
            print('extracting item-sets with ' + str(k) + ' items ....')
            
            '''
            Divide data into many parts and create processes to generate frequent item-sets
            '''
            L_k = HashTable()
            chunks = L_k1.split(nthreads)
            processes = []
            
            C_ks = []
            BaseManager.register("AprioriHash", HashTable)
            manager = BaseManager()
            manager.start()
            C_ks.append(manager.AprioriHash())
            
            index = 0
            for L_k_1_chunk in chunks:
                process_i = Process(target = Apriori.generate_Lk, 
                                    args=(min_sup, L_k_1_chunk,C_ks[index], k))
                processes.append(process_i)
                index += 1
            
            # wait for all thread completes
            for process_i in processes:
                process_i.start()
                process_i.join()
             
            '''
            Merge results which returns from processes
            '''
            for new_C_k in C_ks:
                L_k.append(new_C_k)
            L_k1.clear()
            L_k1 = L_k
    
            '''
            Append frequent item-sets with k items to file
            '''
            freq_itemsets_dict = L_k1.generate_itemset_dictionary()
            
            print ('Writing frequent itemset to file ' + str(freq_itemsets_dict.size()))
            freq_itemsets_dict.ntransactions = nTransactions
            freq_itemsets_dict.save_2_file(output_file, 'a', write_support)
            freq_itemsets_dict.clear()
            
            k += 1
            
        print ('stop at k = ' + str(k))
     
    @staticmethod
    def generate_Lk_vw(min_sup, L_k1, C_k_file, k):
        print('generate candidates with ' + str(k) + ' items')
        file_writer = open(C_k_file, 'w') 
        for key, hash_item_collection in L_k1.get_items():
            for index in range(hash_item_collection.size() - 1):
                
                index_th_item = hash_item_collection.get_item(index)
                new_key = ''
                if key == '':
                    new_key = index_th_item.last_item
                else:
                    new_key = key +',' + index_th_item.last_item
                new_hash_collection = HashItemCollection()
                
                #check if it is infrequent item-set
                for item in hash_item_collection.get_items_from(index + 1):
                    new_item = HashItem(item.last_item)
                    inter_items = set(index_th_item.tids).intersection(item.tids)      
                    if len(inter_items) >= min_sup:  
                        new_item.add_tids(list(inter_items))
                        new_hash_collection.add_item(new_item)
                        
                if new_hash_collection.size() > 0:  
                    file_writer.write(new_key)
                    file_writer.write('\n')
                    file_writer.write(new_hash_collection.serialize())      
                    file_writer.write('\n')
        file_writer.close()

    def generate_frequent_itemsets_vw(self, min_sup, nThreads, end, output_file):
        
        '''
        Step 1: Generate frequent item-sets with 1 item and write to file
        '''
        ntransactions = self.data_set.size()
        with open(output_file, 'w') as text_file:
            text_file.write(str(ntransactions))
            text_file.write('\n')
        
        
        self.generate_L1(min_sup)
        self.L1.generate_itemset_dictionary_vw(output_file, 'a')
        
        '''
        Step 2: Generate frequent item-sets with more than 1 item and append to the file
        '''
        k = 2    
        L_k1 = self.L1
        
        while not L_k1.is_empty() and (end == -1 or k <= end):
            
            print('extracting item-sets with ' + str(k) + ' items ....')
            
            '''
            Divide data into many parts and create processes to generate frequent item-sets
            '''
            chunks = L_k1.split(nThreads)
            L_k1 = None
            processes = []
            
            index = 0
            for L_k_1_chunk in chunks:
                chunk_output_file = self.freq_itemsets_tmp_file +'.'+ str(index)
                process_i = Process(target = Apriori.generate_Lk_vw, 
                                    args=(min_sup, L_k_1_chunk,chunk_output_file, k))
                processes.append(process_i)
                index += 1
            
            # wait for all thread completes
            for process_i in processes:
                process_i.start()
                process_i.join()
             
            '''
            Merge results which returns from processes
            '''
            L_k1 = HashTable()
            for index in range(len(chunks)):
                chunk_input_file = self.freq_itemsets_tmp_file +'.'+ str(index)
                L_k1.deserialize(chunk_input_file, False)
            
            '''
            Append frequent item-sets with k items to file
            '''
            print ('Writing frequent itemset to file....')
            x = L_k1.generate_itemset_dictionary_vw(output_file, 'a')
            print ('#item-sets: ' + str(x))
            k += 1
            
        print ('stop at k = ' + str(k))

    def get_item_interaction_matrix(self):
        self.generate_L1(0)
        items_dict = self.L1.generate_itemset_dictionary()
        items_dict.nTransaction = self.data_set.size()
        
        nItems = items_dict.size()
        dict_item_indexes = items_dict.convert_2_indexes()
            
        A = np.zeros((nItems, nItems))
        for transaction in self.data_set:
            indexes = []
            for item_name in transaction:
                indexes.append(dict_item_indexes[item_name])
            for i in range(len(indexes)):
                for j in range(i+1, len(indexes)):
                    A[indexes[i], indexes[j]] += 1
                    A[indexes[j], indexes[i]] += 1
        return dict_item_indexes, A
    
        
        