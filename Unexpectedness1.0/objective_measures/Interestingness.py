import math

def conditional_probability(both, condition):
    if both == 0:
        return 0
    if condition == 0:
        return float('inf')
    return both/condition

# These objective_measures for rule: left -> right

class ObjectiveMeasure:

    @staticmethod
    def confidence(left, right, both, total, k = 1, m = 1):
        return conditional_probability(both, left)
    
    @staticmethod
    def coverage(left, right, both, total, k = 1, m = 1):
        return left/total
    
    @staticmethod
    def prevalence(left, right, both, total, k = 1, m = 1):
        return right/total
    
    @staticmethod
    def recall(left, right, both, total, k = 1, m = 1):
        return conditional_probability(both, right)
    
    @staticmethod
    def specificity(left, right, both, total, k = 1, m = 1):
        not_both = total - (left + right - both)
        not_left = total - left
        return conditional_probability(not_both, not_left)
    
    @staticmethod
    def accuracy(left, right, both, total, k = 1, m = 1):
        not_both = total - (left + right - both)
        return both/total + not_both/total
    
    @staticmethod
    def lift(left, right, both, total, k = 1, m = 1):
        return conditional_probability(both, left) * (right/total)

    @staticmethod
    def leverage(left, right, both, total, k = 1, m = 1):
        return conditional_probability(both, left) - (left/total) * (right/total)
    
    @staticmethod
    def change_of_support(left, right, both, total, k = 1, m = 1):
        return conditional_probability(both, left) - right/total
    
    @staticmethod
    def relative_risk(left, right, both, total, k = 1, m = 1):
        not_left = total - left
        right_not_left = right - both
        
        x = conditional_probability(both, left) 
        y = conditional_probability(right_not_left, not_left)
        if x == 0: return 0
        if y == 0: return float('inf')
        return x/y 
    
    @staticmethod
    def jaccard(left, right, both, total, k = 1, m = 1):
        return both/(left + right - both)
    
    @staticmethod
    def certainty_factor(left, right, both, total, k = 1, m = 1):
        p_right = right/total
        x = (conditional_probability(both, left) - p_right)
        y = (1 - p_right)
        if x == 0: return 0
        if y == 0: return float('inf')
        return x/y
    
    @staticmethod
    def odd_ratio(left, right, both, total, k = 1, m = 1):
        not_both = total - (left + right - both)
        if (both == 0 or not_both == 0): return 0
        if left == both or right == both: return float('inf')
        return (both / (left - both)) * (not_both/(right - both))
    
    @staticmethod
    def yuleQ(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_not_both = 1 - (left + right - both)/total
        p_left_not_right = (left - both)/total
        p_right_not_left = (right - both)/total
        
        x = (p_both * p_not_both - p_left_not_right * p_right_not_left)
        y = (p_both * p_not_both + p_left_not_right * p_right_not_left)
        if x == 0: return 0
        if y == 0: return float('inf')
        return x/y
    
    @staticmethod
    def yuleY(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_not_both = 1 - (left + right - both)/total
        p_left_not_right = (left - both)/total
        p_right_not_left = (right - both)/total
        x = math.sqrt(p_both * p_not_both) - math.sqrt(p_left_not_right * p_right_not_left)
        y = math.sqrt(p_both * p_not_both) + math.sqrt(p_left_not_right * p_right_not_left)
        if x == 0: return 0
        if y == 0: return float('inf')
        return x/y
    
    @staticmethod    
    def klosgen(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_right = right/total
        return math.sqrt(p_both) * (conditional_probability(both, left) - p_right)
    
    @staticmethod
    def conviction(left, right, both, total, k = 1, m = 1):
        p_left_not_right = (left - both)/total
        x = (left/total) * ((total - right)/total)
        if x == 0: return 0
        if p_left_not_right == 0:
            return float('inf')
        return x / p_left_not_right
    
    @staticmethod    
    def weighting_dependancy(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_left = left/total
        p_right = right/total
        
        return (math.pow(p_both/(p_left * p_right), k) - 1) * math.pow(p_both, m)
    
    @staticmethod
    def collective_strength(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_left = left/total
        p_right = right/total
        
        p_not_both = 1 - (left + right - both)/total
        p_not_left = 1 - p_left
        p_not_right = 1 - p_right
        
        a = (p_both + conditional_probability(p_not_both, p_not_left))
        b = (p_left*p_right + p_not_left * p_not_right)
        c = (1 - p_left * p_right - p_not_left * p_not_right)
        d = (1 - p_both - conditional_probability(p_not_both, p_not_left))
        if a == 0 or c == 0: return 0
        if b == 0 or d == 0: return float ('inf')
        return (a * c)/(b * d)
    
    @staticmethod
    def laplace_correction(left, right, both, total, k = 1, m = 1):
        return (both + 1)/(left + 2)
    
    @staticmethod
    def gini_index(left, right, both, total, k = 1, m = 1):
        p_left = left/total
        p_right = right/total
        p_not_left = 1 - p_left
        p_not_right = 1 - p_right
        
        p_right_con_left = conditional_probability(both, left)
        p_not_right_con_left = conditional_probability(left - both, left)
        p_right_con_not_left = conditional_probability(right - both, total - left)
        p_not_right_con_not_left = conditional_probability(total - left - right + both, total - left)
        
        x = p_left * (math.pow(p_right_con_left, 2) + math.pow(p_not_right_con_left, 2))
        y = p_not_left * (math.pow(p_right_con_not_left, 2) + math.pow(p_not_right_con_not_left, 2))
        return x + y - math.pow(p_right, 2) - math.pow(p_not_right, 2)
    
    @staticmethod
    def jmeasure(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_right_con_left = conditional_probability(both, left)
        p_left_not_right = (left - both)/total
        p_not_right_con_left = conditional_probability(left - both, left)
        p_right = right/total
        p_not_right = 1 - p_right
        
        x = p_both * math.log(p_right_con_left/p_right)
        if p_left_not_right != 0: 
            x += p_left_not_right * math.log(p_not_right_con_left/p_not_right)
        return  x
      
    @staticmethod
    def one_way_support(left, right, both, total, k = 1, m = 1):
        p_right_con_left = conditional_probability(both, left)
        p_both = both/total
        p_left = left/total
        p_right = right/total
        
        return p_right_con_left * math.log2(p_both/(p_left * p_right))
     
    @staticmethod    
    def two_way_support(left, right, both, total, k = 1, m = 1):   
        p_both = both/total
        p_left = left/total
        p_right = right/total
        
        return p_both * math.log2(p_both/(p_left * p_right))
    
    @staticmethod
    def two_ways_support_variation(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_left = left/total
        p_right = right/total
        
        p_left_not_right = (left - both)/total
        p_not_right = 1 - p_right
        
        p_right_not_left = (right - both)/total
        p_not_left = 1 - p_left
        
        p_not_left_not_right = 1 - (left + right - both)/total
        
        x = p_both * math.log2(p_both/(p_left * p_right));
        if p_left_not_right != 0:
            x += p_left_not_right * math.log2(p_left_not_right/(p_left * p_not_right))
        if p_right_not_left != 0:
            x += p_right_not_left * math.log2(p_right_not_left/(p_not_left * p_right))
        if p_not_left_not_right != 0:
            x += p_not_left_not_right * math.log2(p_not_left_not_right/(p_not_left*p_not_right))
        return x
    
    @staticmethod
    def linear_correlation_coefficient(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_left = left/total
        p_right = right/total
        
        if p_left == 1 or p_right == 1: return float('inf')
        return (p_both - p_left * p_right)/math.sqrt(p_left * p_right * (1-p_left) * (1 - p_right))
    
    @staticmethod
    def piatetsky_shapiro(left, right, both, total, k = 1, m = 1):
        return (both/total) - (left/total) * (right/total)
    
    @staticmethod
    def cosine(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_left = left/total
        p_right = right/total
        
        return p_both/math.sqrt(p_left * p_right)
    
    @staticmethod
    def loevinger(left, right, both, total, k = 1, m = 1):
        p_left_not_right = (left - both)/total
        p_left = left/total
        p_not_right = 1 - right/total
        
        if p_left_not_right == 0: return float('inf')
        return 1 - (p_left * p_not_right)/p_left_not_right
    
    @staticmethod
    def information_gain(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_left = left/total
        p_right = right/total
        return math.log(p_both/(p_left * p_right))
    
    @staticmethod
    def sebag_schoenauner(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_left_not_right = (left  - both)/total
        if p_left_not_right == 0: return float('inf')
        return p_both/p_left_not_right
    
    @staticmethod
    def least_contradiction(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_left_not_right = (left  - both)/total
        p_right = right/total
        return (p_both - p_left_not_right)/p_right
    
    @staticmethod
    def odd_multiplier(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_left_not_right = (left  - both)/total
        p_right = right/total
        
        if p_left_not_right == 0: return float('inf')
        return (p_both * (1 - p_right))/(p_right * p_left_not_right)
    
    @staticmethod
    def counter_example_rate(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_left_not_right = (left  - both)/total
        return 1 - (p_left_not_right/p_both)
    
    @staticmethod
    def zhang(left, right, both, total, k = 1, m = 1):
        p_both = both/total
        p_left_not_right = (left  - both)/total
        p_left = left/total
        p_right= right/total
        p_not_right = 1 - p_right
        
        x = p_both * p_not_right
        y = p_right * p_left_not_right
        if x < y: 
            x = y
        if x == 0: return float('inf')
        return (p_both - p_left * p_right)/x