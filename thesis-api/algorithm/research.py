import pandas as pd
import helpers.lda as lda
import helpers.nsga2 as nsga2
from helpers.terminator import HVTermination
import numpy as np
import helpers.other_helpers as h
import helpers.preprocessing as pp
from ast import literal_eval
from pymoo.factory import get_crossover, get_mutation, get_sampling, get_performance_indicator
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2
import glob
import time

pd.options.mode.chained_assignment = None  # default='warn'

def get_optimization_result(backlog, user_experience_vector, storypoints):

	backlog["issue_similarity"] = backlog.apply(lambda x: h.cosine_similarity_with_intersection(user_experience_vector, x["vector"]), axis = 1)
 
	backlog["novelty"] = backlog.apply(lambda x: h.calculate_novelty(user_experience_vector, x["vector"]), axis = 1)
 
	businessvalue_array = backlog["businessvalue"].to_numpy()
  
	issue_similarity_array = backlog["issue_similarity"].to_numpy()
 
	novelty_array = backlog["novelty"].to_numpy()
 
	problem = nsga2.get_problem(businessvalue_array, issue_similarity_array, novelty_array, storypoints)

	algorithm = NSGA2(
		pop_size=200,
		sampling=get_sampling("bin_random"),
		crossover=get_crossover("bin_hux"),
		mutation=get_mutation("bin_bitflip"),
		eliminate_duplicates=True,
  	)

	res = minimize(problem,
		algorithm, 
  		HVTermination(10, 0.001),
		verbose=False,
  		save_history=True)
 
	return res

def save_lda_models():
	dataset = pd.read_csv('./thesis-api/dataset/preprocessed_dataset.csv', encoding='utf-8')

	dataset["preprocessed_text"] = dataset["preprocessed_text"].apply(literal_eval)

	grouped_projects = dataset.groupby("project")

	for project, project_df in grouped_projects: 
		
		done = h.get_done_issues(project_df)

		number_of_topics, alpha, beta = h.get_hyperparameters(project)

		lda_model, dictionary = lda.get_lda_model(done, number_of_topics, alpha, beta)
		
		lda_model.save("./thesis-api/algorithm/lda_models/" + project)

		dictionary.save("./thesis-api/algorithm/lda_dicts/" + project)
		
	
def save_results():
	dataset = pd.read_csv('./thesis-api/dataset/preprocessed_dataset.csv', encoding='utf-8')

	dataset["preprocessed_text"] = dataset["preprocessed_text"].apply(literal_eval)

	grouped_projects = dataset.groupby("project")

	for project, project_df in grouped_projects: 
		
		if (project not in ["COMPASS"]):
			continue

		print(project)
  
		lda_start_time = time.time()
  
		done = h.get_done_issues(project_df)

		backlog = h.get_backlog_issues(project_df)

		number_of_topics, alpha, beta = h.get_hyperparameters(project)

		lda_model, dictionary = lda.get_lda_model(done, number_of_topics, alpha, beta)
		
		backlog = lda.add_topic_vector_to_baclog_issues(backlog, lda_model, dictionary, number_of_topics)
  
		lda_end_time = time.time()
  
		lda_execution_time = lda_end_time - lda_start_time
  
		results = {
			'project': [],
			'assignee': [],
			'hypervolume': [],
			'opt_execution_time': [],
			'lda_execution_time': [],
			'velocity': []
			}

		grouped_users = done.groupby("assignee.name")

		for user, user_df in grouped_users: 
			if user not in ["durran.jordan", "anna.herlihy"]:
				continue

			print(user)
		
			if (len(user_df.index) < 1):
				continue
   
			velocity = h.get_velocity(user_df)
   
			if velocity < 1:
				continue

			opt_start_time = time.time()

			vector = lda.get_user_experience_topic_vector(user_df, lda_model, dictionary, number_of_topics)

			res = get_optimization_result(backlog, vector, velocity)
   
			print(res.F)
   
			hv_indicator = get_performance_indicator("hv", ref_point=np.array([1.1, 1.1, 1.1]))
 
			hypervolume =  hv_indicator.do(res.F)
   
			opt_end_time = time.time()

			opt_execution_time = opt_end_time - opt_start_time

			results['project'].append(project)
			results['assignee'].append(user)
			results['hypervolume'].append(hypervolume)
			results['velocity'].append(velocity)
			results['opt_execution_time'].append(opt_execution_time)
			results['lda_execution_time'].append(lda_execution_time)
			print(results["hypervolume"])
						
		# pd.DataFrame(results).to_csv('./thesis-api/algorithm/validation/' + project.lower() + '.csv', index=False)



def weighted_average(dataframe, value, weight):
    val = dataframe[value]
    wt = dataframe[weight]
    return (val).sum() / wt.sum()


def result_stats():
		
	df_list = [pd.read_csv(filename) for filename in glob.glob("./thesis-api/algorithm/validation/*.csv")]
	
	df = pd.concat(df_list, axis=0)
 
	df["weighted_hv"] = df["hypervolume"] / df["velocity"]
 
	grouping = df.groupby("project")
 
	wt_average = grouping.apply(weighted_average, "hypervolume", 'velocity')
 
	grouped = grouping.agg(Min=("weighted_hv", np.min), Max=("weighted_hv", np.max),Std=("weighted_hv", np.std))
 
	grouped["Weighted Avg"] = wt_average
 
	grouped["% from best HV"] = (grouped["Weighted Avg"] / grouped["Max"]) * 100
 
	grouped = grouped.round(2)

	pd.DataFrame(grouped).to_csv('./thesis-api/algorithm/validation/grouped/mean_project_hv_test.csv')
 
def performance_stats():
	df_list = [pd.read_csv(filename) for filename in glob.glob("./thesis-api/algorithm/validation/*.csv")]

	df = pd.concat(df_list, axis=0)

	grouping = df.groupby("project")

	aggregated = grouping.agg(lda_s=("lda_execution_time", np.min), max_opt_s=("opt_execution_time", np.max), min_opt_s=("opt_execution_time", np.min), mean_opt_s=("opt_execution_time", np.mean), std_opt_s = ("opt_execution_time", np.std))

	dataset = pd.read_csv('./thesis-api/dataset/preprocessed_dataset.csv', encoding='utf-8')
 
	backlog = h.get_backlog_issues(dataset)
 
	aggregated['backlog'] = backlog.groupby("project").size()
 
	done = h.get_done_issues(dataset)
 
	aggregated['done'] = done.groupby("project").size()
 
	aggregated = aggregated.round(2)
 
	pd.DataFrame(aggregated).to_csv('./thesis-api/algorithm/validation/grouped/project_execution_time_test.csv')
 
   
def issue_counts():
	dataset = pd.read_csv('./thesis-api/dataset/jiradataset_issues_v1.4.csv', encoding='utf-8')

	total = dataset.groupby("project").size().reset_index(name ='total')

	dataset = pp.add_backlog_completed_flag(dataset)

	total_after_pp = dataset.groupby("project").size().reset_index(name ='after_pp')

	done_for_each_project = h.get_done_issues(dataset).groupby("project").size().reset_index(name ='done')

	backlog_for_each_project = h.get_backlog_issues(dataset).groupby("project").size().reset_index(name ='backlog')

	grouped = dataset.groupby("project")

	dictinary = {}
	projects = []
	dev_counts = []
	for project, df in grouped:
		devs = df.groupby("assignee.name").size().reset_index(name ='total')
		dev_counts.append(len(devs))
		projects.append(project)
  
	dictinary["project"] = projects
 
	dictinary["devs"] = dev_counts
 
	dates = grouped.agg(From = ("created", np.min), To = ("created", np.max))
  
	dev_df = pd.DataFrame.from_dict(dictinary, orient="columns")
 
	df = pd.merge(total, total_after_pp, on="project", right_index = True,
				left_index = True, )

	df = pd.merge(df, done_for_each_project, on="project",right_index = True,
				left_index = True)

	df = pd.merge(df, backlog_for_each_project, on="project",right_index = True,
				left_index = True)
 
	df = pd.merge(df, dev_df, on="project",right_index = True,
				left_index = True)
 
	df = pd.merge(df, dates, on="project",right_index = True,
				left_index = True)
 
	df["From"] = pd.to_datetime(df['From'], utc=True)
	df["To"] = pd.to_datetime(df['To'], utc=True)
 
	df["From"] = df["From"].apply(lambda x: x.date())
	df["To"] = df["To"].apply(lambda x: x.date())
 
	df.set_index('project', inplace=True)

	df.to_csv("./thesis-api/algorithm/validation/grouped/issue_counts.csv")
  
if __name__ == '__main__':
	# save_results()
	# result_stats()
	# performance_stats()
	# issue_counts()
 	save_lda_models()