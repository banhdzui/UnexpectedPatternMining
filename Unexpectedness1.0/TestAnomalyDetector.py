'''
Created on 19 Feb 2018

@author: danhbuithi
'''
import sys
import numpy as np

from common.IOHelper import IOHelper
from common.CommandArgs import CommandArgs
from common.DataSet import DataSet
from rules_mining.AssociationRule import AssociationRule

from sklearn.metrics.ranking import roc_curve, auc
from sklearn.metrics.classification import f1_score
from sklearn.svm.classes import SVC
from sklearn.ensemble.forest import RandomForestClassifier

def refine_with_unexpectedness(data_set, classes_dict, preY, Ytrue, unexpected_rules):
    
    print('Refine with unexpected rules...')
    y_pred = np.copy(preY)
    for i in range(data_set.size()):
        x = data_set.get_transaction(i)
        for r in unexpected_rules:
            if r.satisfy_rule(x, is_lhs = True):
                label = r.right_items[0]
                y_pred[i] = classes_dict[label]
    print(f1_score(Ytrue, y_pred, average=None))
    if (data_set.number_of_classes() <= 2):
        fpr, tpr, _ = roc_curve(Ytrue, y_pred.flatten())
        print(auc(fpr, tpr))
    
def filter_association_rules(unexpected_rules, delta_1 = 0):
    rules = []
    for x in unexpected_rules:
        if x[2][0][1] > delta_1: 
            rules.append(AssociationRule.string_2_rule(x[0]))
    return rules
        
if __name__ == '__main__':
    config = CommandArgs({'train'   : ('', 'Path of train data.'),
                          'test'    : ('', 'Paht of test data.'),
                          'rules'   : ('', 'Path of unexpected rules.'),
                          'class'   : (0, 'Index of class in data.')
                          })    
    
    if not config.load(sys.argv):
        print ('Argument is not correct. Please try again')
        sys.exit(2)
        
    print('Loading data....')
    class_index = int(config.get_value('class'))
    train_data_set = DataSet()
    train_data_set.load(config.get_value('train'), class_index, has_header = False)
    X_train, Y_train = train_data_set.convert_2_binary_format()
        
    test_data_set = DataSet()
    test_data_set.load(config.get_value('test'), class_index, has_header = False)
    Xtest, Ytest = test_data_set.convert_2_binary_format_with(X_train.item_dict, Y_train.item_dict)
    Ytest = Ytest.flatten()
    
    class_count = train_data_set.number_of_classes()
    
    unexpected_rules = IOHelper.load_json_object(config.get_value('rules'))
    refined_unexpected_rules = filter_association_rules(unexpected_rules)
    
    print('svm testing...')
    svc_model = SVC(kernel = 'poly', degree=3, coef0 = 0.1, random_state = 1)
    svc_model.fit(X_train.relation_matrix, Y_train.values.flatten())
    
    svc_y_pred = svc_model.predict(Xtest)
    print(f1_score(Ytest, svc_y_pred, average=None))
    if (class_count <= 2):
        fpr, tpr, _ = roc_curve(Ytest, svc_y_pred.flatten())    
        print(auc(fpr, tpr))

    refine_with_unexpectedness(test_data_set, Y_train.item_dict, svc_y_pred, Ytest, refined_unexpected_rules)
    
    
    print('Random forest testing...')
    rf_model = RandomForestClassifier(n_estimators=20, random_state=1)
    rf_model.fit(X_train.relation_matrix, Y_train.values.flatten())
    
    rf_y_pred = rf_model.predict(Xtest)
    print(f1_score(Ytest, rf_y_pred, average=None))
    if (class_count <= 2):
        fpr, tpr, _ = roc_curve(Ytest, rf_y_pred.flatten())
        print(auc(fpr, tpr))
    
    refine_with_unexpectedness(test_data_set, Y_train.item_dict, rf_y_pred, Ytest, refined_unexpected_rules)
    