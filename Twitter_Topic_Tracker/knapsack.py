from queue import Queue
from functools import lru_cache
from queue import PriorityQueue
from collections import deque
import collections
import numpy as np



def knapsack(items, maxweight):
    """Solve the knapsack problem by finding the most valuable subsequence
    of items that weighs no more than maxweight.

    items must be a sequence of pairs (value, weight), where value is a
    number and weight is a non-negative integer.

    maxweight is a non-negative integer.

    Return a pair whose first element is the sum of values in the most
    valuable subsequence, and whose second element is the subsequence.

    >>> items = [(4, 12), (2, 1), (6, 4), (1, 1), (2, 2)]
    >>> knapsack(items, 15)
    (11, [(2, 1), (6, 4), (1, 1), (2, 2)])

    """
    @lru_cache(maxsize=None)
    def bestvalue(i, j):
        # Return the value of the most valuable subsequence of the first
        # i elements in items whose weights sum to no more than j.
        if j < 0:
            return float('-inf')
        if i == 0:
            return 0
        value, weight, index = items[i - 1]
        return max(bestvalue(i - 1, j), bestvalue(i - 1, j - weight) + value)

    j = maxweight
    result = []
    for i in reversed(range(len(items))):
        if bestvalue(i + 1, j) != bestvalue(i, j):
            result.append(items[i])
            j -= items[i][1]
    result.reverse()
    return sum([i for (i,j,k) in result]), sum([j for (i,j,k) in result]), [k for (i,j,k) in result]

#items must be a sequence of pairs (value, weight)
items = [(4, 12, 0), (2, 1, 1), (6, 4, 2), (1, 1, 3), (0, 0, 4)]
print(knapsack(items, 8))
utility_cost = [(0.1, 0.8, 1), (0.9, 0.2, 2), (0.7, 0.5, 3), (0.0, 0.01, 4)]
print(knapsack(utility_cost, 0.9))
print(knapsack(utility_cost, 2.3))
print(knapsack(utility_cost, 100))


def logit_np(x):
    a = []
    for p in x:
        a.append(np.log((p  + 2900)/5800 ) - np.log(1 - (p + 2900) /5800))
    if len(a) > 0:
        return a
    elif len(a) == 1:
        return a[0]
    else:
        return None


tag_counts1 =  [251.771997690695, 2513.1058834676264, 0, 1618.568735753377, 906.2973753359659, 0, 1325.1812085549848, 0, 1247.829376587997]
print('knapsack cost: ', logit_np(tag_counts1))

tag_counts2 =  [1379.2045324186245, 0, 0, 0, 0, 0, 0, 0, 0]
print('knapsack cost: ', logit_np(tag_counts2))

tag_counts2 =  [2500.2045324186245]
print('knapsack cost: ', logit_np(tag_counts2))


class Cost_Value_Estimator:
       
#     def __init__(self):
    def __init__(self, max_iteration):                           
        self.MAX_ITERATION = max_iteration
        self.tag_value_queues = {}
                           
    def get_ucb_estimate(self):

        n_tot = 0
        costs = []
        values = []
        out_tags = []

        for tag, tag_value_queue in self.tag_value_queues.items():
            tag_total_value = 0
            tag_total_count = 0
            if len(tag_value_queue) != 0:

                iteration_values = []
                iteration_counts = []
                for iteration_values_cost in tag_value_queue:
                    for (value, count) in iteration_values_cost:
                        n_tot += count 
                        iteration_values.append(value)
                        iteration_counts.append(count)                    

                values.append(np.mean(iteration_values))
                costs.append(np.sum(iteration_counts))
                out_tags.append(tag)

        cost_estimate= np.array(logit_np(np.array(costs)))
        ucb_value_estimate = np.array(values) + np.sqrt(2*np.log(n_tot)/(np.array(costs) + 0.001))

        print('ucb_value_estimate: ', ucb_value_estimate )
        knapsack_terms = []
        cost_value = []
        
        ucb_value_estimate_sorted_index = np.argsort(ucb_value_estimate)[::-1]
        for i in range(0, 10): # take to only
            if i < len(ucb_value_estimate):
                sortend_index = ucb_value_estimate_sorted_index[i]
                tag = out_tags[sortend_index]
                value_estimate = ucb_value_estimate[sortend_index]
    #             if value_estimate > 0.01: # some threshold for how many is hundred will make it useful
                cost = cost_estimate[sortend_index]
                cost_value.append((cost, value_estimate , len(cost_value)))
                knapsack_terms.append(tag)

        return knapsack_terms, cost_value


    def get_cost_value_based_on_mean_value(self):


        n_tot = 0
        costs = []
        values = []
        out_tags = []

        for tag, tag_value_queue in self.tag_value_queues.items():
            tag_total_value = 0
            tag_total_count = 0
            if len(tag_value_queue) != 0:

                iteration_values = []
                iteration_counts = []
                for iteration_values_cost in tag_value_queue:
                    for (value, count) in iteration_values_cost:
                        n_tot += count 
                        iteration_values.append(value)
                        iteration_counts.append(count)                    

                values.append(np.mean(iteration_values))
                costs.append(np.sum(iteration_counts))
                out_tags.append(tag)

        cost_estimate= np.array(logit_np(np.array(costs)))
        mean_value_estimate = np.array(values)
        
        print('mean_value_estimate: ', mean_value_estimate)

        knapsack_terms = []
        cost_value = []
        mean_value_estimate_sorted_index = np.argsort(mean_value_estimate)[::-1]
        for i in range(0, 10): # take to only
            if i < len(mean_value_estimate):
                sortend_index = mean_value_estimate_sorted_index[i]
                tag = out_tags[sortend_index]
                value_estimate = mean_value_estimate[sortend_index]
    #             if value_estimate > 0.01: # some threshold for how many is hundred will make it useful
                cost = cost_estimate[sortend_index]
                cost_value.append((cost, value_estimate , len(cost_value)))
                knapsack_terms.append(tag)

        return knapsack_terms, cost_value



    def update_tag_queue(self, tag_values_update):  
#         self.reduce_tag_queue() # call reduce before every update

        # update new iteration values

        for tag, value in tag_values_update.items():
            if tag in self.tag_value_queues:
                self.tag_value_queues[tag].append(value)
    #             print('added ', tag)
            else:
                tag_value_queue = deque(maxlen= self.MAX_ITERATION)
                tag_value_queue.append(value)
                self.tag_value_queues[tag] = tag_value_queue
                
        # The below step removes the stale entries after MAX_ITERATION
        for tag, __ in self.tag_value_queues.items():
            if tag not in tag_values_update:
                self.tag_value_queues[tag].append([])
                
        self.remove_empty_tag()
                
    def remove_empty_tag(self):   
        to_be_popped = []
        for tag, tag_value_queue in self.tag_value_queues.items():
            if len(tag_value_queue) != 0:
                total_values_len  = 0
                for values in tag_value_queue:
                    for value in values:
                        total_values_len += len(value)
#                 print('tag: ', tag, total_values_len)
                if total_values_len ==0:
                    to_be_popped.append(tag)

            else:
                to_be_popped.append(tag)

        for tag in to_be_popped:
            self.tag_value_queues.pop(tag, None)
    #         print('popped ', tag)

    def print_tag_value_queues(self):
        print('Printing Queue \n')
        for tag, value_queues in self.tag_value_queues.items():
#             for i, elem in enumerate(value_queues):                   # iterate over the deque's elements
            print(tag, value_queues)
#             print(tag, value_queues.queue)
    

cost_value_estimator = Cost_Value_Estimator(1)    
# these are (value, count) for tweets    
tag_values_update = {'t1': [(0.2, 1), (0.1, 2), (0.3, 1)],
                  't2': [(0.2, 2), (0.5, 3), (0.7, 1)], 
                  't3':[(0.2, 3), (0.4, 4), (0.7, 4)],
                  't4': [(1.0, 1), (0.0, 2), (0.0,2) , (0.0, 4)]}   

cost_value_estimator.update_tag_queue( tag_values_update)
cost_value_estimator.print_tag_value_queues()
print('mean_value_estimate: ', cost_value_estimator.get_cost_value_based_on_mean_value())
print('ucb_estimate: ', cost_value_estimator.get_ucb_estimate())


tag_values_update = {'t5':  [(0.2, 1), (0.1,2)],                  't2': [(0.2, 3), (0.5, 5), (0.7, 3)], 
                  't3':[(0.2, 4), (0.5, 5)],
                  't6': [(1.0, 4), (0.0, 4), (0.0, 5) , (0.0, 4) ]} 

cost_value_estimator.update_tag_queue(tag_values_update)
cost_value_estimator.print_tag_value_queues()
print('mean_value_estimate: ', cost_value_estimator.get_cost_value_based_on_mean_value())
print('ucb_estimate: ', cost_value_estimator.get_ucb_estimate())
