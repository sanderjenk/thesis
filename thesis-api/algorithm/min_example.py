
import autograd.numpy as anp
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
from pymoo.factory import get_crossover, get_mutation, get_sampling, get_performance_indicator
from ast import literal_eval
import pandas as pd

import numpy as np

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

if __name__ == '__main__':    
    storypoints = [1, 2, 1]
    businessvalue = [4, 3, 2]
    issue_similarity = [0.8, 0.7, 0.5]
    novelty = [0, 0, 1]
    problem = get_problem(storypoints, businessvalue, issue_similarity, novelty, 3)
    res = get_optimization_result(problem)
    print(res.F)
    print(res.algorithm.opt.get("F"))
    best_solution_indices = res.X.astype(np.int)
    
    hv = get_performance_indicator("hv", ref_point=np.array([1, 1, 1]))
    print("hv", hv.do(res.F), res.X.astype(np.int))
    print("hv", hv.do(res.pop[0].F), res.pop[0].X.astype(np.int))
    print("hv", hv.do(res.pop[1].F), res.pop[1].X.astype(np.int))
    print("hv", hv.do(res.pop[2].F), res.pop[2].X.astype(np.int))
    pass
    
    # dataset = pd.read_csv('./thesis-api/dataset/preprocessed_dataset.csv', encoding='utf-8')
    
    # dataset = pd.read_csv('./thesis-api/dataset/jiradataset_issues_v1.4.csv', encoding='utf-8')


    # # dataset["preprocessed_text"] = dataset["preprocessed_text"].apply(literal_eval)
    
    # df = dataset.loc[(dataset["project"] == "STL") & (dataset["assignee.name"].isna())]
    
    # print(df[["resolution.name", "status.name", "assignee.name"]].head(50))
    
    # grouped = df.groupby("assignee.name")
    
    # for status, frame in grouped:
    #     print(status)
