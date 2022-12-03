# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

large_size_rod_used = 0 
demand_size = [4, 6, 7]
demand_count = [80, 50, 100]
large_len = 15 
effective_len = large_len
waste = 0

for i in range(3):
    while (True):
        if (demand_count[i] > 0) :
            if (demand_size[i] <= effective_len):
                effective_len = effective_len - demand_size[i]
                demand_count[i] = demand_count[i] - 1
            
            else:
                large_size_rod_used = large_size_rod_used + 1
                waste = waste + effective_len
                effective_len = large_len
                continue
        else:
            break
print("large_size_rod_used ", large_size_rod_used)
print("total waste ", waste)
