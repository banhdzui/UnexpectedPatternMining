'''
Created on 27 Feb 2018

@author: danhbuithi
'''

import sys

from common.CommandArgs import CommandArgs
from sampling.RandomSplitter import RandomSplitter
from common.IOHelper import IOHelper

if __name__ == '__main__':
    config = CommandArgs({'input'   : ('', 'Path of input data'),
                          'test'   : ('', 'Path of test data.'),
                          'train'   : ('', 'Path of train data'),
                          'rate'    : ('', 'Rating of data')
                          })    
    
    if not config.load(sys.argv):
        print ('Argument is not correct. Please try again')
        sys.exit(2)
        
    rate = float(config.get_value('rate'))
    train, test = RandomSplitter.split(config.get_value('input'), rate)
    IOHelper.write_file_in_lines(config.get_value('train'), train)
    IOHelper.write_file_in_lines(config.get_value('test'), test)
    
    print('Finished!!!')