# -*- coding: utf-8 -*-

import cplex
import sys
import numpy as np

# Input data

DEBUG = True
class DATA:
    n= 100 # number of large-sized rod 
    m = 3 # number of required rod types
    small_rod_demands = [80,50,100]
    small_rod_size = [4.,6.,7.]
    large_rod_size = [15.0]
    
class CPLEX:
    
    
    def __init__(self):
        self.model = cplex.Cplex()
        self.sub_created = False
        
    def solve_model(self, master_flag):
        
        if master_flag:
            self.model.set_problem_type(self.model.problem_type.LP) # you need to specify the type of model, else it will take MIP
        else:
            self.model.set_problem_type(self.model.problem_type.MILP)
        
        self.model.solve()
        
    def write_problem(self, file_name):
        self.model.write(file_name)

    
    def get_objective_value(self):

        return self.model.solution.get_objective_value()
    
    def get_solution(self):
        
        return self.model.solution.get_values()
    
    
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
        

    
    def define_constraint_by_row(self, the_const_names, the_rows, the_senses, my_rhs ):
        
        self.model.linear_constraints.add(lin_expr=the_rows, senses= the_senses, rhs = my_rhs, names = the_const_names)
        
        
    
    def get_dual(self):
        
        return self.model.solution.get_dual_values()
    
    def get_pattern(self,pattern_lot,n_const):
        
        return [[self.model.linear_constraints.get_coefficients(i,j) for i in range(n_const)] 
                for j in range(len(pattern_lot)) if pattern_lot[j]!=0]
        
    
    def create_sub_generate_pattern(self, coef_multiplier, n_var, large_rod_size, small_rod_size):
        
        if not self.sub_created:
            self.var_name = ["y_"+str(i) for i in range(n_var)]
            self.model.variables.add(obj=coef_multiplier,types=[self.model.variables.type.integer]*n_var,
                               names=self.var_name)
            
            row = [[self.var_name,small_rod_size]]
            the_senses = 'L'
            const_name = 'P'
            self.model.linear_constraints.add(lin_expr=row,senses=[the_senses], rhs = large_rod_size, 
                                             names= [const_name])
            
            self.model.objective.set_sense(self.model.objective.sense.maximize)
            
            self.sub_created = True
        
        self.model.objective.set_linear([(i,coef_multiplier[i]) for i in range(n_var)])
        
        self.model.solve(False) # For solving a subproblem, Pass False as argument, True is for Master 
        
        if self.get_objective_value() > 1: # Since min reduced cost = 1 - dual*variable <0:  max dual*variable - 1 >0 => max dual*variable >1
            
            return self.model.solution.get_values()
        else:
            return []
                
    def update_master(self, pattern,iteration, n_const):
        
        # add a variable to master
        self.model.variables.add(obj=[1],types=[self.model.variables.type.continuous],
                               names=['y_'+str(iteration)], columns=[[[i for i in range(n_const)],pattern]])
        


class cutting_stock_column_generation:
    
    def __init__(self, n, m, small_rod_demands,small_rod_size,large_rod_size):
        
        self.n = n
        self.m = m
        self.small_rod_demands = small_rod_demands
        self.small_rod_size = small_rod_size
        self.large_rod_size = large_rod_size
        
        self.master_flag = True
        self.initial_pattern = np.identity(m) # different demand types are m
        
        # initialize restricted master 
        self.int_var_pattern_count = ["y_"+str(i) for i in range(m)] 
        self.const_names_types = ["t_"+str(j) for j in range(m)] 
        self.const_sense_types = ["G" for j in range(m)] 
        self.const_rhs_types = small_rod_demands

        self.cplexSolver1 = CPLEX() # For master
        self.cplexSolver2 = CPLEX() # For sub
    
    def create_restricted_master_model(self):    
        
        # 1. number of types of patterns
        objective_coef_vector = [1 for i in range(self.m)]
        self.cplexSolver1.define_variable(self.int_var_pattern_count, "continuous", objective_coef_vector)
    
        
        # add constraints
        #1. const_names_types
        for i in range(self.m):
            the_rows = [[self.int_var_pattern_count, list(self.initial_pattern[i])]]
            self.cplexSolver1.define_constraint_by_row([self.const_names_types[i]], 
                                                             the_rows, [self.const_sense_types[i]],
                                          [self.const_rhs_types[i]])
        
    def iterative_loop(self, WRITE_DEBUG):
        
        # get the dual values of the initial restricted master:
        # solve the initial master
        objvalue =0.
        dual_value = self.cplexSolver1.get_dual()
        pattern = self.cplexSolver2.create_sub_generate_pattern(dual_value, self.m, self.large_rod_size, 
                                                               self.small_rod_size )
        
        if WRITE_DEBUG:
            self.cplexSolver1.write_problem("initial_master.LP")
            self.cplexSolver2.write_problem("initial_sub.LP")
        column =  self.m
        while(pattern):
            if pattern:
                
                self.cplexSolver1.update_master(pattern,column, self.m)
                self.cplexSolver1.solve_model(self.master_flag)
                dual_value = self.cplexSolver1.get_dual()
                pattern = self.cplexSolver2.create_sub_generate_pattern(dual_value,self.m, self.large_rod_size, 
                                                                       self.small_rod_size )
                column = column + 1
                if WRITE_DEBUG:
                    self.cplexSolver1.write_problem("initial_master_"+str(column - self.m)+".LP")
                    self.cplexSolver2.write_problem("initial_sub_"+str(column - self.m)+".LP")
                
            else:
                objvalue =  self.cplexSolver1.get_objective_value()
                break
        return objvalue, pattern
    
    def solve_the_model_master(self):
        # Now time to solve it
        self.cplexSolver1.solve_model(self.master_flag)
        
    def get_solution(self):
        return self.cplexSolver1.get_solution()
        
    def get_objective_value(self):
        # Get the objective function. - which is number of large-sized rod
        return self.cplexSolver1.get_objective_value()
        
    def get_pattern(self,pattern_lot):
        
        # Get columns
        return self.cplexSolver1.get_pattern(pattern_lot, self.m)

if __name__ == "__main__":
    WRITE_DEBUG = True
    if len(sys.argv) != 2:
        print("Data is not provided accuratly, solving a cutting stock problem from the default-example")
        cs = cutting_stock_column_generation(DATA.n, DATA.m, DATA.small_rod_demands,DATA.small_rod_size, DATA.large_rod_size)
        # Create the model
        cs.create_restricted_master_model()
        #if DEBUG:
         #   cs.write_the_model_master("initial_restricted_master.LP")
        
        cs.solve_the_model_master()
        cs.iterative_loop(WRITE_DEBUG)
        
        # obtain the value
        print("optimal rod used", int(cs.get_objective_value()))
        
        pattern_lot = cs.get_solution()
        print("optimal pattern lot", cs.get_solution())
        
        print("optimal pattern", cs.get_pattern(pattern_lot))
    else:
        extract_data_from_input_file = sys.argv[1]
        print(extract_data_from_input_file)
