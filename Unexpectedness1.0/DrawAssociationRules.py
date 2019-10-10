'''
Created on Jun 21, 2017

@author: BanhDzui
'''

import json
import sys

from common.CommandArgs import CommandArgs

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#from sklearn.decomposition.kernel_pca import KernelPCA
from sklearn.decomposition.incremental_pca import IncrementalPCA

def load_feature_vectors(input_file):
    features = []
    association_rules = []
    
    with open(input_file, 'r') as feature_reader:
        feature_reader.readline()
        feature_reader.readline()
        for line in feature_reader:
            rule_text, f_vector = json.loads(line.strip())
            association_rules.append(rule_text)
            features.append(f_vector)
    return np.array(features), association_rules

def load_clusters(input_file):
    
    number_of_cluster = -1
    clusters_dict = {}
    with open(input_file, 'r') as clusters_reader:
        for line in clusters_reader:
            sub_strings = line.split('\'')
            rule_text = sub_strings[1].strip('(\' ')
            temp = sub_strings[2].split(',')
            
            cluster_id = int(temp[1])
            clusters_dict[rule_text] = cluster_id
            
            if cluster_id > number_of_cluster: number_of_cluster = cluster_id
    return clusters_dict, cluster_id + 1

import colorsys

def get_N_HexCol(N=5):

    HSV_tuples = [(x * 1.0 / N, 1, 1) for x in range(N)]
    hex_out = []
    for rgb in HSV_tuples:
        rgb = map(lambda x: int(x * 255), colorsys.hsv_to_rgb(*rgb))
        hex_out.append('#%02x%02x%02x' % tuple(rgb))
    #print(hex_out)
    return hex_out

            
if __name__ == '__main__':
    config = CommandArgs({'feature'     : ('', 'Path of features file'),
                          'cluster'      : ('', 'Path of clusters file'),
                          'output'      : ('', 'Path of output file'),
                          'title'       : ('Dataset', 'Title of charts')
                          })
    
    if not config.load(sys.argv):
        print ('Argument is not correct. Please try again')
        sys.exit(2)
        
    X, association_rules = load_feature_vectors(config.get_value('feature'))
    
    m = 2
    print('dimensional reduce: ' + str(m))
    
    pca = IncrementalPCA(n_components = X.shape[1]//m)
    new_X = pca.fit_transform(X)
    clusters, number_of_clusters = load_clusters(config.get_value('cluster'))
    print (number_of_clusters)
    
    unique_colors = get_N_HexCol(number_of_clusters + 1)
    Y = []
    for rule in association_rules:
        cluster_id = clusters[rule]
        Y.append(unique_colors[cluster_id + 1])
    
    
    #plt.scatter(new_X[:,0], new_X[:,1], c = np.array(Y), alpha = 0.9, s = 10)
    #plt.title(config.get_value('title'))
    #plt.savefig(config.get_value('output'), format='PNG',bbox_inches='tight')
    
    #np.array(Y)
    fig = plt.figure()
    #plt.title(config.get_value('title'))
    ax = fig.gca(projection='3d')
    ax.text2D(0.5, 0.95, config.get_value('title'), transform=ax.transAxes)
    ax.scatter(new_X[:,0], new_X[:,1], new_X[:,2], c = Y, alpha = 0.9, s = 5)
    plt.savefig(config.get_value('output'), format='PNG',bbox_inches='tight')
    #plt.show()
    