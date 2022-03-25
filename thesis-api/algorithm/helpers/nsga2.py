
import autograd.numpy as anp
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.factory import get_crossover, get_mutation, get_sampling
from pymoo.visualization.scatter import Scatter

class Issues(Problem):
    def __init__(self,
                 n_items,  # number of items that can be picked up
                 S,  # story points of each issue
                 B,  # business value of each issue
                 I,  # Issue similarity to user experience
                 N,  # Issue novelty
                 C,  # maximum story points
                 ):
        super().__init__(n_var=n_items, n_obj=1, n_constr=1, xl=0, xu=100, type_var=bool)

        self.S = S
        self.B = B
        self.I = I
        self.N = N
        self.C = C

    def _evaluate(self, x, out, *args, **kwargs):
        f1 = - anp.sum(self.B * x, axis=1)
        f2 = - anp.sum(self.I * x, axis=1)
        f3 = - anp.sum(self.N * x, axis=1)

        out["F"] = anp.column_stack([f1, f2, f3])
        out["G"] = (anp.sum(self.S * x, axis=1) - self.C)
        
def get_problem(storypoints, businessvalue, issue_similarity, novelty, max_story_points):
    
    return Issues(len(storypoints), storypoints, businessvalue, issue_similarity, novelty, max_story_points)

def get_optimization_result(problem):
    
    algorithm = NSGA2(
        pop_size=200,
        sampling=get_sampling("bin_random"),
        crossover=get_crossover("bin_hux"),
        mutation=get_mutation("bin_bitflip"),
        eliminate_duplicates=True)

    res = minimize(problem,
        algorithm,
        ('n_gen', 100),
        verbose=False)
    
    return res