
import autograd.numpy as anp
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

# initial problem that just optimizes business value
class Issues(Problem):
    def __init__(self,
                 n_items,  # number of items that can be picked up
                 W,  # story points of each issue
                 P,  # priority of each issue
                 C,  # maximum story points
                 ):
        super().__init__(n_var=n_items, n_obj=1, n_constr=1, xl=0, xu=100, type_var=bool)

        self.W = W
        self.P = P
        self.C = C
	
    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = -anp.sum(self.P * x, axis=1)
        out["G"] = (anp.sum(self.W * x, axis=1) - self.C)


def get_optimization_result(backlog_issues_df, max_story_points):
    problem = Issues(backlog_issues_df.shape[0],backlog_issues_df["storypoints"].to_numpy(), backlog_issues_df["businessvalue"].to_numpy(), max_story_points)

    algorithm = NSGA2(pop_size=20)

    res = minimize(problem,
                algorithm,
                ('n_gen', 1000),
                seed=2,
                verbose=False)

    return res