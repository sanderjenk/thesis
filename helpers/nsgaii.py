
from turtle import back
import numpy as np
import autograd.numpy as anp

from pymoo.core.problem import Problem

class Knapsack(Problem):
    def __init__(self,
                 n_items,  # number of items that can be picked up
                 W,  # weights for each item
                 P,  # profit of each item
                 C,  # maximum capacity
                 ):
        super().__init__(n_var=n_items, n_obj=1, n_constr=1, xl=0, xu=1, type_var=bool)

        self.W = W
        self.P = P
        self.C = C

    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = -anp.sum(self.P * x, axis=1)
        out["G"] = (anp.sum(self.W * x, axis=1) - self.C)


class MultiObjectiveKnapsack(Knapsack):
    def __init__(self, *args):
        super().__init__(*args)

    def _evaluate(self, x, out, *args, **kwargs):
        f1 = - anp.sum(self.P * x, axis=1)
        f2 = anp.sum(x, axis=1)

        out["F"] = anp.column_stack([f1, f2])
        out["G"] = (anp.sum(self.W * x, axis=1) - self.C)


def create_random_knapsack_problem(n_items, seed=1, variant="single"):
    anp.random.seed(seed)
    P = anp.random.randint(1, 100, size=n_items)
    W = anp.random.randint(1, 100, size=n_items)
    C = int(anp.sum(W) / 10)

    if variant == "single":
        problem = Knapsack(n_items, W, P, C)
    else:
        problem = MultiObjectiveKnapsack(n_items, W, P, C)

    return problem

# initial problem that just optimizes priority
class Issues(Problem):
    def __init__(self,
                 n_items,  # number of items that can be picked up
                 W,  # story points of each issue
                 P,  # priority of each issue
                 C,  # maximum story points
                 ):
        super().__init__(n_var=n_items, n_obj=1, n_constr=1, xl=0, xu=1, type_var=bool)

        self.W = W
        self.P = P
        self.C = C
	
    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = -anp.sum(self.P * x, axis=1)
        out["G"] = (anp.sum(self.W * x, axis=1) - self.C)

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.factory import get_problem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter

def get_optimal_solution(backlog_issues_df, max_story_points):
	try:
		problem = Issues(backlog_issues_df.shape[0],backlog_issues_df["storypoints"].to_numpy(), backlog_issues_df["priority"].to_numpy(), max_story_points)

		algorithm = NSGA2(pop_size=100)

		res = minimize(problem,
					algorithm,
					('n_gen', 200),
					seed=1,
					verbose=False)

		print(res.X, res.G, res.F, res.opt, res.pop)
	except Exception as e:
		print(e)

	