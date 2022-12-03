# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 19:57:22 2022

@author: devii
"""

import cplex
import sys

# Input data

DEBUG = True
class DATA:
    n= 100 # number of large-sized rod 
    m = 3 # number of required rod types
    small_rod_demands = [80,50,100]
    small_rod_size = [4,6,7]
    large_rod_size = [15]

class CPLEX:
    
    
    def __init__(self):
        self.model = cplex.Cplex()
        
    def solve(self):
    
        self.model.solve()
        
    def read_problem(self, problem):
    
        return cplex.Cplex(problem)
    
    def write(self, file_name):
        self.model.write(file_name)

    def get_objective_value(self):

        return self.model.solution.get_objective_value()
    
    
    def define_variable(self, varname_list, type_of_var, objective_coef_vector):
        
        n_var = len(varname_list)
        if type_of_var == "binary":
             self.model.variables.add(obj=objective_coef_vector , names =varname_list,
                        types = [self.model.variables.type.binary] * n_var )
             
        elif type_of_var == "continuous":
            self.model.variables.add(obj= objective_coef_vector, names =varname_list,
                        types = [self.model.variables.type.continuous] * n_var)
            
        elif type_of_var == "integer":
            self.model.variables.add(obj= objective_coef_vector, names =varname_list,
                        types = [self.model.variables.type.integer] * n_var)
        return None

    def define_constraint(self, the_const_names, the_rows, the_senses, my_rhs ):
        
        self.model.linear_constraints.add(lin_expr=the_rows, senses= the_senses, rhs = my_rhs, names = the_const_names)
        
        return None


class cutting_stock:
    
    def __init__(self, n, m, small_rod_demands,small_rod_size,large_rod_size):
        
        self.n = n
        self.m = m
        self.small_rod_demands = small_rod_demands
        self.small_rod_size = small_rod_size
        self.large_rod_size = large_rod_size

        self.bin_var_names = ["y_"+str(i) for i in range(n)] # binary variables
        self.int_var_name_types = [["x_"+str(i)+"_"+str(j) for j in range(n)] for i in range(m)]
        self.const_names_types = ["t_"+str(j) for j in range(m)] 
        self.const_sense_types = ["G" for j in range(m)] 
        self.const_rhs_types = small_rod_demands


        self.const_name_pattern = ["p_"+str(i) for i in range(n)]
        self.const_sense_pattern = ["L" for i in range(n)]
        self.const_rhs_pattern  = [0 for i in range(n)]
        
        self.cplexSolver = CPLEX()
    def create_mathematical_model(self):
        
        
        
        # 1. binary variable
        objective_coef_vector = [1 for i in range(self.n)]
        self.cplexSolver.define_variable(self.bin_var_names, "binary", objective_coef_vector)
    
        # 2. integer variable
        for i in range(self.m):
            objective_coef_vector = [0 for i in range(self.n)]
            self.cplexSolver.define_variable(self.int_var_name_types[i], "integer", objective_coef_vector)
    
        # add constraints
        #1. const_names_types
        for i in range(self.m):
            the_rows = [[self.int_var_name_types[i], [1 for i in range(self.n)]]]
            self.cplexSolver.define_constraint([self.const_names_types[i]], the_rows, [self.const_sense_types[i]],
                                          [self.const_rhs_types[i]])
    
        #2 const_name_pattern
        coef_list =  self.small_rod_size + [-self.large_rod_size[0]]
        for j in range(self.n):
            temp_var_name_list = []
            for i in range(self.m):
                temp_var_name_list.append(self.int_var_name_types[i][j])
    
            the_rows = [temp_var_name_list + [self.bin_var_names[j]] ,coef_list]
            self.cplexSolver.define_constraint([self.const_name_pattern[j]], [the_rows], 
                              [self.const_sense_pattern[j]], [self.const_rhs_pattern[j]])
    
    def solve_the_model(self):
        # Now time to solve it
        self.cplexSolver.solve()
        
    def write_the_model(self):
        self.cplexSolver.write("cutting_stock_integer.LP")
        
    def get_objective_value(self):
        # Get the objective function. - which is number of large-sized rod
        return self.cplexSolver.get_objective_value()
        


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Data is not provided accuratly, solving a cutting stock problem from the default-example")
        cs = cutting_stock(DATA.n, DATA.m, DATA.small_rod_demands,DATA.small_rod_size, DATA.large_rod_size)
        # Create the model
        cs.create_mathematical_model()
        if DEBUG:
            cs.write_the_model()
        
        # Solve it
        cs.solve_the_model()
        
        # obtain the value
        print("optimal rod used", int(cs.get_objective_value()))
    else:
        extract_data_from_input_file = sys.argv[1]
        print(extract_data_from_input_file)
