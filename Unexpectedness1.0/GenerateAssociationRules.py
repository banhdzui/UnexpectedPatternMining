'''
Created on 30 Oct 2017

@author: danhbuithi
'''
import sys

from common.CommandArgs import CommandArgs
from common.DataSet import DataSet

from rules_mining.RuleMiner import RuleMiner
from common.ArgumentTuple import ARMParams
        
    
if __name__ == '__main__':
    config = CommandArgs({'input'   : ('', 'Path of data-set file'),
                          'format'  : ('spect', 'Format of input data'),
                          'minsup'  : (0.1, 'Minimum support'),
                          'minconf' : (0.3, 'Minimum confidence'),
                          'maxitems': (-1, 'Maximum number of items in the rules'),
                          'class'   : (-1, 'Class index')
                          })    
    
    if not config.load(sys.argv):
        print ('Argument is not correct. Please try again')
        sys.exit(2)
        
    print('Loading data....')
    train_data_set = DataSet()
    class_index = int(config.get_value('class'))
    train_data_set.load(config.get_value('input'), class_index)
    
    print('Generating rules ....')
    
    minsup = float(config.get_value('minsup'))
    minconf = float(config.get_value('minconf'))
    itemset_max_size = int(config.get_value('maxitems'))
    arm_params = ARMParams(minsup, minconf, itemset_max_size)
    
    miner = RuleMiner(config.get_value('format'), train_data_set)
    miner.generate_itemsets_and_rules(arm_params)
    
    print('Finished!!!')
    
    