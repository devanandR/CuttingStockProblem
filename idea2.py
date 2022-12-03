# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np

large_size_rod_used = 0 
demand_size = [4, 6, 7]
number_of_demand_type = 3
demand_count = [80, 50, 100]
large_len = 15 
effective_len = large_len
waste = 0

def indices_of_sorted_list(s):
    return sorted(range(len(s)), key=lambda k: s[k])

# np_demand_size = np.array(demand_size)
for i in indices_of_sorted_list(demand_size):
    while (True):
        if (demand_count[i] > 0) :
            if (demand_size[i] <= effective_len):
                effective_len = effective_len - demand_size[i]
                demand_count[i] = demand_count[i] - 1
                while(True):
                    temp_remaining = [(effective_len - demand_size[j],j) for j in range(number_of_demand_type) 
                                      if  effective_len >= demand_size[j] and demand_count[j]>0]
                    if temp_remaining:
                        j = np.argmin(np.array([x[0] for x in temp_remaining]))
                        j = [x[1] for x in temp_remaining][j]
                        effective_len =  effective_len - demand_size[j]
                        demand_count[j] = demand_count[j] - 1
                    else:
                        break
                
            large_size_rod_used = large_size_rod_used + 1
            waste = waste + effective_len
            effective_len = large_len
            continue
        else:
            break
print("large_size_rod_used ", large_size_rod_used)
print("total waste ", waste)
