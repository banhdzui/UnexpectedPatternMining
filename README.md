# Unexpected Pattern Mining
Mining unexpected patterns from the data. The patterns are association rules which are generated using Apriori Algorithm. A clustering based framework is used to categorized these patterns into clusters, which are considered as beliefs, and outliers, which are potential candidates for unexpected patterns. The outliers then are compared to the beliefs to see if they're contrary or not contrary to the beliefs. If they are, they are considered as unexpected.

## Requirements:
- Python 3.x
- numpy
- scipy
- sklearn
- mpl_toolkits

## Running program
### Generation of  unexpected patterns
#### Step 1: Generate association rules:
Run the script 'GenerateAssociationRules.py' with following arguments: input, minsup, minconf. The rules and their feature vectors are saved in 'tmp' folder.

Ex: Breast Cancer dataset
```
python GenerateAssociationRules.py --input in/breast_train_transactions.txt --minsup 0.01 --minconf 0.8
```
#### Step 2: Detect unexpected rules:
Run the script 'DetectUnexpectedRules.py' for clustering and detecting unexpected rules from the rules which are generated in step 1. The arguments include: minpts, eps, delta1, delta2, output. Clustering result are saved in the file which is specifized by 'output' agurment and the expected rules are saved in <output>.unexpected file.

Ex: Breast Cancer dataset
```
python DetectUnexpectedRules.py  --output out/breast_clusters.txt --minpts 3 --eps 1.0 --delta1 0.0 --delta2 -0.9
```
#### Step 3(optional) Evaluate the rules.
This step is to examine the contribution of the unexpected rules to the performance of two classifiers: Random Forest and SVM.

Run the script 'TestAnomalyDetector.py' with the following arguments: train (training data), test (testing data), rules (file saving unexpected rules), class (index of 'class' feature in data)

Ex: Breast Cancer dataset
```
python TestAnomalyDetector.py --train in/breast_train_transactions.txt --test in/breast_test_transactions.txt --rules out/breast_clusters.txt.unexpected --class 0
```
### Visualization of the clustering result
Run the script 'DrawAssociationRules.py' with the arguments: feature (file saving rules and their features), cluster (clustering result file), output and title.

Ex: Breast Cancer dataset
```
pythonw DrawAssociationRules.py --feature tmp/miner.tmp.non_redundant_rules --cluster out/breast_clusters.txt --output out/breast_cancer.png --title Breast_Cancer
```


