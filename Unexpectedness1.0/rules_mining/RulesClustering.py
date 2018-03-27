'''
Created on May 3, 2017

@author: BanhDzui
'''
from sklearn.metrics.pairwise import euclidean_distances
import numpy as np

class MyRulesClustering(object):
    
    def __init__(self, eps, minpts, nThreads, sample_features):
        self.eps = eps
        self.minpts = minpts
        self.nthreads = nThreads
        self.sample_features = sample_features
        
        m, _ = self.sample_features.shape
        self.Y = [-1 for _ in range(m)]
        self.visisted = [False for _ in range(m)]
        
    def region_query(self, p):
        temp = self.sample_features[p,:]
        temp = np.reshape(temp, (1, -1))
        #distance = cosine_distances(temp, self.sample_features)
        distance = euclidean_distances(temp, self.sample_features)
        neighbors = np.where(distance <= self.eps)
        return neighbors[1].tolist()
    
    def expand_cluster(self, p, C, neighbors):
        self.Y[p] = C
        while len(neighbors) > 0:
            other_p = neighbors.pop(0)
            if self.visisted[other_p] == False:
                self.visisted[other_p] = True
                other_neighbors = self.region_query(other_p)
                
                if (len(other_neighbors) >= self.minpts):
                    neighbors.extend(other_neighbors)
                    tmp = list(set(neighbors))
                    neighbors.clear()
                    neighbors.extend(tmp)
                    
            if self.Y[other_p] == -1:
                self.Y[other_p] = C
                
         
    
    def run(self):
        C = -1
        m, _ = self.sample_features.shape
        print(m)
        for p in range(m):
            if p % 50 == 0: print (p)
            #print(str(p) + '###' + str(C))
            if self.visisted[p] == True: continue
            
            self.visisted[p] = True
            neighbors = self.region_query(p)
            if len(neighbors) >= self.minpts:
                C += 1
                self.expand_cluster(p, C, neighbors)
        
                
class ClusteringEngine(object):
    
    def __init__(self, X_train):
        self.sample_features = X_train 

        
    def run_dbscan(self, my_eps, my_min_samples, number_of_threads):
        print ('Doing clustering ....')
        
        db = MyRulesClustering(my_eps, my_min_samples, 
                               number_of_threads,
                               self.sample_features)
        db.run()
        
        n_clusters = len(set(db.Y))- (1 if -1 in db.Y else 0)
        n_noises = db.Y.count(-1)
        
        print('Number of clusters' + str(n_clusters))
        print('Number of noises' + str(n_noises))
    
        return n_clusters, db.Y
                
        