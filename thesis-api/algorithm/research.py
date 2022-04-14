from this import d
import pandas as pd
import helpers.lda as lda
import helpers.nsga2 as nsga2
from helpers.terminator import HVTermination
import numpy as np
import helpers.other_helpers as h
import helpers.preprocessing as pp
from ast import literal_eval
from pymoo.factory import get_crossover, get_mutation, get_sampling, get_performance_indicator
from pymoo.factory import get_crossover, get_mutation, get_sampling
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2
import tqdm
import glob
import time
import matplotlib.pyplot as plt
from wordcloud import WordCloud


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
	
def save_results():
	dataset = pd.read_csv('./thesis-api/dataset/preprocessed_dataset.csv', encoding='utf-8')

	dataset["preprocessed_text"] = dataset["preprocessed_text"].apply(literal_eval)

	grouped_projects = dataset.groupby("project")

	for project, project_df in grouped_projects: 
		
		if (project not in ["COMPASS", "DATACASS"]):
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
		# 	if user not in ["anna.herlihy", "brian.blevins"]:
		# 		continue

			print(user)
		
			if (len(user_df.index) < 1):
				continue
   
			velocity = h.get_velocity(user_df)
   
			if velocity < 1:
				continue

			opt_start_time = time.time()

			vector = lda.get_user_experience_topic_vector(user_df, lda_model, dictionary, number_of_topics)

			res = get_optimization_result(backlog, vector, velocity)
   
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
						
		pd.DataFrame(results).to_csv('./thesis-api/algorithm/validation/' + project.lower() + '.csv', index=False)

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

	pd.DataFrame(grouped).to_csv('./thesis-api/algorithm/validation/grouped/mean_project_hv.csv')
 
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
 
	pd.DataFrame(aggregated).to_csv('./thesis-api/algorithm/validation/grouped/project_execution_time.csv')
 
def plot_number_of_topics_hypervolume():
	params_df = pd.read_csv('./thesis-api/algorithm/lda_tuning_results/lda_params.csv', encoding='utf-8')

	params_df = params_df.loc[params_df["project"] != "mdl"]
	hv_df = pd.read_csv('./thesis-api/algorithm/validation/grouped/mean_project_hv.csv', encoding='utf-8')
 
	plt.figure(figsize=(7, 5))
	plt.scatter(params_df["topics"], hv_df["Weighted Avg"],  facecolor="red", edgecolor='black', marker="o")
	for i, label in enumerate(hv_df["project"].tolist()):
		plt.annotate(label, (params_df["topics"].tolist()[i], hv_df["Weighted Avg"].tolist()[i]))
	plt.title("Number of topics in relation to hypervolume")
	plt.xlabel("Topics")
	plt.ylabel("Hypervolume")
	plt.savefig('./thesis-api/algorithm/validation/plots/topics_hypervolume_plot.png')
 
def barchart():
	hv_df = pd.read_csv('./thesis-api/algorithm/validation/grouped/mean_project_hv.csv', encoding='utf-8')
	plt.figure(figsize=(7, 5))
	plt.bar(hv_df["project"], hv_df["Weighted Avg"])
	plt.xticks(rotation=90)
	plt.ylabel("Weighted average of hypervolume")
	plt.title("Weighted average hypervolume of projects")
	plt.gcf().subplots_adjust(bottom=0.18)

	plt.savefig('./thesis-api/algorithm/validation/bar_hypervolume.png')
 
def plot_performance_velocity():
	projects = pd.read_csv('./thesis-api/algorithm/validation/grouped/project_execution_time.csv', encoding='utf-8')
	df_list = [pd.read_csv(filename) for filename in glob.glob("./thesis-api/algorithm/validation/*.csv")]

	df = pd.concat(df_list, axis=0)
 
	projects.set_index('project', inplace=True)

 
	test = projects["mean_opt_s"].to_dict()
 
	df["mean_opt_s"] = df["project"].map(test)
 
	df["y"] = (df["opt_execution_time"] / df["mean_opt_s"]) * 100
 
	plt.scatter(df["velocity"], df["y"],  facecolor="red", edgecolor='black', marker=".")

	plt.xlabel("Velocity")
	plt.ylabel("Dev. opt. time percentage from project mean")
	plt.savefig('./thesis-api/algorithm/validation/plots/scatter_opt_velocity.png')
 
def plot_performance_lda():
	df = pd.read_csv('./thesis-api/algorithm/validation/grouped/project_execution_time.csv', encoding='utf-8')

	plt.figure(figsize=(7, 5))
 
	donelist = df["done"].tolist()
 
	ldalist = df["lda_s"].tolist()
 
	plt.scatter(df["done"], df["lda_s"],  facecolor="red", edgecolor='black', marker="o")
 
	for i, label in enumerate(df["project"].tolist()):
		plt.annotate(label, (donelist[i], ldalist[i]))
  
	plt.xlabel("Number of done issues")
	plt.ylabel("LDA training time in seconds")
	plt.savefig('./thesis-api/algorithm/validation/plots/scatter_lda_done.png')
 
def plot_performance_opt():
	df = pd.read_csv('./thesis-api/algorithm/validation/grouped/project_execution_time.csv', encoding='utf-8')

	plt.figure(figsize=(7, 5))
 
	backloglist = df["backlog"].tolist()
 
	optlist = df["mean_opt_s"].tolist()
 
	plt.scatter(df["backlog"], df["mean_opt_s"],  facecolor="red", edgecolor='black', marker="o")
 
	for i, label in enumerate(df["project"].tolist()):
		plt.annotate(label, (backloglist[i], optlist[i]))
  
	plt.xlabel("Number of backlog issues")
	plt.ylabel("Optimization time in seconds")
	plt.savefig('./thesis-api/algorithm/validation/plots/scatter_opt_backlog.png')
 
def generate_word_clouds():
	dataset = pd.read_csv('./thesis-api/dataset/preprocessed_dataset.csv', encoding='utf-8')

	dataset["preprocessed_text"] = dataset["preprocessed_text"].apply(literal_eval)

	grouped_projects = dataset.groupby("project")

	for project, project_df in grouped_projects: 
		
		if (project not in ["DATACASS"]):
			continue

		done = h.get_done_issues(project_df)

		number_of_topics, alpha, beta = h.get_hyperparameters(project)

		lda_model, _ = lda.get_lda_model(done, number_of_topics, alpha, beta)

		for t in range(lda_model.num_topics):
			plt.figure(figsize=(8,3))
			plt.imshow(WordCloud(width = 800, height= 300, background_color= "white").fit_words(dict(lda_model.show_topic(t, 200))))
			plt.axis("off")
			plt.title("Topic #" + str(t+1))
			plt.savefig('./thesis-api/algorithm/validation/plots/wordcloud_' + project + str(t+1) +  '.png')
   
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
	# plot_number_of_topics_hypervolume()
	# barchart()
	# generate_word_clouds()
	# plot_performance_lda()
	# plot_performance_opt()
	# plot_performance_velocity()
	issue_counts()