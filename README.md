# UnexpectedPatternMining
Mining unexpected patterns from the data. The patterns are association rules which are generated using Apriori Algorithm. A clustering based framework is used to categorized these patterns into clusters, which are considered as beliefs, and outliers, which are potential candidates for unexpected patterns. The outliers then are compared to the beliefs to see if they're contrary or not contrary to the beliefs. If they are, they are considered as unexpected.

The program is developed in Python. Here are the requirements to run our program:
- Python 3.x
- numpy
- scipy
- sklearn
- mpl_toolkits

To generate unexpected patterns from the data and evaluate them, you do the the following steps:
Generate association rules: run the script 'GenerateAssociationRules.py' with following arguments: input, format, minsup, minconf
Ex: 'Breast Cancer' dataset
python GenerateAssociationRules.py --input in/breast_train_transactions.txt --format spect --minsup 0.01 --minconf 0.8

- Detect unexpected rules: run the script 'DetectUnexpectedRules.py' with following arguments:

- Evaluate the rules
