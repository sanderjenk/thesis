import pandas as pd
import helpers.preprocessing as pp
import helpers.lda as lda
import helpers.nsga2 as nsga2
import numpy as np
import helpers.other_helpers as h
import algorithm_for_app as app
import os
import sys
from ast import literal_eval

if __name__ == '__main__':
    
    
	# import numpy as np
	# from pymoo.factory import get_problem
	# from pymoo.visualization.scatter import Scatter

	# # The pareto front of a scaled zdt1 problem
	# pf = get_problem("zdt1").pareto_front()

	# # The result found by an algorithm
	# A = pf[::10] * 1.1

	# # plot the result
	# Scatter(legend=True).add(pf, label="Pareto-front").add(A, label="Result").show()
    
    
    
    
    
	dataset = pd.read_csv('./dataset/preprocessed_dataset.csv', encoding='utf-8')
 
	dataset["preprocessed_text"] = dataset["preprocessed_text"].apply(literal_eval)
 
	project = "xd"
 
	username = "grussell"

	project_issues = dataset.loc[dataset["project"] == project]
 
	user_issues = project_issues.loc[project_issues["assignee.name"] == username]

	solution = app.generate_solution_for_user("xd", project_issues, user_issues, 15)
 
	print(solution.shape[0])

	








