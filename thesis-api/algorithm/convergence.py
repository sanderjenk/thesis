from operator import ge
import pandas as pd
import helpers.preprocessing as pp
import helpers.lda as lda
import helpers.nsga2 as nsga2
from helpers.terminator import HVTermination
import numpy as np
import helpers.other_helpers as h
from ast import literal_eval
from pymoo.factory import get_crossover, get_mutation, get_sampling, get_performance_indicator
import matplotlib.pyplot as plt
from pymoo.indicators.hv import Hypervolume
from pymoo.factory import get_crossover, get_mutation, get_sampling, get_termination
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2

pd.options.mode.chained_assignment = None  # default='warn'

def get_result(backlog, user_experience_vector, storypoints, generations):
	backlog["issue_similarity"] = backlog.apply(lambda x: h.cosine_similarity_with_intersection(user_experience_vector, x["vector"]), axis = 1)
 
	backlog["novelty"] = backlog.apply(lambda x: h.calculate_novelty(user_experience_vector, x["vector"]), axis = 1)
 
	businessvalue_array = backlog["businessvalue_normalized"].to_numpy()
 
	storypoints_array = backlog["storypoints"].to_numpy()
 
	issue_similarity_array = backlog["issue_similarity"].to_numpy()
 
	novelty_array = backlog["novelty"].to_numpy()
 
	problem = nsga2.get_problem(storypoints_array, businessvalue_array, issue_similarity_array, novelty_array, storypoints)

	algorithm = NSGA2(
		pop_size=200,
		sampling=get_sampling("bin_random"),
		crossover=get_crossover("bin_hux"),
		mutation=get_mutation("bin_bitflip"),
		eliminate_duplicates=True,
  	)
 
	if (generations):     
		termination = get_termination("n_gen", 300)
	else:
		termination = HVTermination(10, 0.001)

	res = minimize(problem,
		algorithm,
		termination,
		verbose=False,
		save_history=True) 
	return res


def figure_out_convergence(generations = False):
	dataset = pd.read_csv('./thesis-api/dataset/preprocessed_dataset.csv', encoding='utf-8')

	dataset["preprocessed_text"] = dataset["preprocessed_text"].apply(literal_eval)

	grouped_projects = dataset.groupby("project")

	for project, project_df in grouped_projects: 
		
		# if (project in ["COMPASS", "DATACASS", "FAB", "IS", "MOBILE", "STL", "apstud", "mesos", "tistud", "timob", "mule", "nexus", "dnn", "FAB"]):
		if (project  in ["MDL"]):
			continue
		
		print(project)
		
		done = h.get_done_issues(project_df)

		backlog = h.get_backlog_issues(project_df)

		grouped_users = project_df.groupby("assignee.name")

		number_of_topics, alpha, beta = h.get_hyperparameters(project)

		lda_model, dictionary = lda.get_lda_model(done, number_of_topics, alpha, beta)
		
		backlog = lda.add_topic_vector_to_baclog_issues(backlog, lda_model, dictionary, number_of_topics)

		for user, user_df in grouped_users: 
		
			if (len(user_df.index) < 5):
				continue

			vector = lda.get_user_experience_topic_vector(user_df, lda_model, dictionary, number_of_topics)
   
			res = get_result(backlog, vector, 15, generations)
   
			n_evals = []             # corresponding number of function evaluations\
			hist_F = []              # the objective space values in each generation
			hist_cv = []             # constraint violation in each generation
			hist_cv_avg = []         # average constraint violation in the whole population

			for algo in res.history:

				# store the number of function evaluations
				n_evals.append(algo.evaluator.n_eval)

				# retrieve the optimum from the algorithm
				opt = algo.opt

				# store the least contraint violation and the average in each population
				hist_cv.append(opt.get("CV").min())
				hist_cv_avg.append(algo.pop.get("CV").mean())

				# filter out only the feasible and append and objective space values
				feas = np.where(opt.get("feasible"))[0]
				hist_F.append(opt.get("F")[feas])
   
			approx_ideal = res.F.min(axis=0)
			approx_nadir = res.F.max(axis=0)
   
			metric = Hypervolume(ref_point= np.array([1.1, 1.1, 1.1]))

			hv = [metric.do(_F) for _F in hist_F]
   
			# k = np.where(np.array(hist_cv_avg) <= 0.0)[0].min()
   

			plt.figure(figsize=(7, 5))
			plt.plot(range(0, len(res.history)), hv,  color='black', lw=0.7, label="Avg. CV of Pop")
			plt.scatter(range(0, len(res.history)), hv,  facecolor="none", edgecolor='black', marker="p")
			# plt.axvline(k, color="red", label="All Feasible", linestyle="--")

			plt.title("Convergence")
			plt.xlabel("Generations")
			plt.ylabel("Hypervolume")
			plt.savefig('./thesis-api/algorithm/convergence2/' + project + '.png')
   
			# print(f"Whole population feasible in Generation {k} after {n_evals[k]} evaluations.")

			break
  
if __name__ == '__main__':
	figure_out_convergence(False)
	