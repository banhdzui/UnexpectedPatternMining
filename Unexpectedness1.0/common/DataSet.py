
# Transaction databases, each transaction is a set of items
import numpy as np
from scipy import sparse
from scipy import stats
from common.RelationArray import RelationArray2D
from common.RelationArray import RelationArray1D

class DataSet:
    def __init__(self):
        self.current = 0
        self.train_data = []
        self.data_labels = []
        
    
    def __iter__(self):
        return iter(self.train_data)
                
    def size(self):
        return len(self.train_data)
    
    def get_transaction(self, index):
        return self.train_data[index]
    
    def clear(self):
        self.train_data.clear()
        
    def add_transaction(self, t):
        return self.train_data.append(t) 
        
    '''
    Load data set from a file. The input file must be formated in CSV (comma separated)
    class_index is used in the case of data-set with labels. 
    '''
    def load(self, file_path, class_index = -1, has_header = False):
        self.train_data = []
        if class_index != -1: self.data_labels = []
        
        with open(file_path, "r") as text_in_file:
            if has_header == True:
                text_in_file.readline()
                
            for line in text_in_file:
                transaction = [x.strip() for x in line.split(',')]
                transaction = list(filter(None, transaction))
                
                if (class_index != -1):
                    self.data_labels.append(transaction[class_index])
                    del transaction[class_index]
                
                self.train_data.append(list(set(transaction)))

    '''
    Return number of classes in data (if have).
    '''            
    def number_of_classes(self):
        if self.data_labels == None: return 0
        return len(set(self.data_labels))

    def convert_data_labels(self, inlier_name):
        Y_train = np.zeros(len(self.data_labels))
        for i in range(Y_train.shape[0]):
            if self.data_labels[i] == inlier_name:
                Y_train[i] = 1
            else: 
                Y_train[i] = -1
        return Y_train

    def convert_2_binary_format_with(self, items_dict, classes_dict = None):
        n_items = len(items_dict)
        X_train = np.zeros((self.size(), n_items))
        
        k = 0
        for transaction in self.train_data:
            for item in transaction:
                if item not in items_dict: 
                    print('not in features...')
                    continue
                i = items_dict[item]
                X_train[k, i] = 1.0
            k += 1
            
        Y_train = []
        if classes_dict is not None:
            for label in self.data_labels:
                if label not in classes_dict:
                    print('not in classes')
                    Y_train.append(-1)
                else:
                    Y_train.append(classes_dict[label]) 
        return X_train, np.array(Y_train)        
    
    def get_items_dict_(self):
        attr_dict = {}
        #check existing data
        for transaction in self.train_data:
            for index in range (len(transaction)):
                item_name = transaction[index]
                if item_name not in attr_dict:
                    attr_dict[item_name] = True
        return attr_dict
    
    def get_class_list_(self):
        # Sort items and classes in alphabet order.
        return sorted(set(self.data_labels))
        
        

    '''
    Convert transaction data into binary format
    '''
    def convert_2_binary_format(self):
        
        attr_dict = self.get_items_dict_()
         
        # Sort items and classes in alphabet order.
        classes_list = sorted(set(self.data_labels))
        items_list = sorted(attr_dict.keys())
        
        classes_dict = {classes_list[i] : i for i in range(len(classes_list))}
        attr_dict = {items_list[i] : i for i in range(len(items_list))}
        
        #Generate binary matrix (X_train) and array of labels(Y_train)
        X_train, Y_train = self.convert_2_binary_format_with(attr_dict, classes_dict)
                
        return RelationArray2D(attr_dict, sparse.csr_matrix(X_train)), RelationArray1D(classes_dict, np.array(Y_train))
        
    @staticmethod
    def write_relation_matrix_(matrix):
        with open('item_relation.csv', 'w') as file_writer:
            item_names = sorted(matrix.item_dict.keys())
            file_writer.write('o0o,')
            file_writer.write(','.join(item_names))
            file_writer.write('\n')
            for i in range(len(item_names)):
                file_writer.write(item_names[i] + ',')
                file_writer.write(','.join(str(x) for x in matrix.relation_matrix[i].tolist()))
                file_writer.write('\n')
                
                
   
    '''
    This method estimates relationship among items. There're two kinds of relationship
    - Correlation:including negative correlation (<= -0.3) and positive correlation (>= 0.3)
    - Cover: threshold 1.0, including cover (2) and covered (-2) 
    '''
    def items_relationship(self):
        
        print ('Computing item relation matrix...')
        
        X_train, _ = self.convert_2_binary_format()
    
        correlation_matrix, p_values = stats.spearmanr(X_train.relation_matrix.todense(), axis = 0)
        
        zeros_mask = (p_values <= 0.05).astype(int)
        small_mask = (np.abs(correlation_matrix) >= 0.1).astype(int)
        
        relation_matrix = correlation_matrix * small_mask * zeros_mask
        
        a = RelationArray2D(X_train.item_dict, relation_matrix)
        DataSet.write_relation_matrix_(a)
        
        return a