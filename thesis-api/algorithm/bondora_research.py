from cProfile import label
import pandas as pd
import helpers.lda as lda
import helpers.nsga2 as nsga2
from helpers.terminator import HVTermination
import numpy as np
import helpers.other_helpers as h
import helpers.preprocessing as pp
from pymoo.factory import get_crossover, get_mutation, get_sampling, get_performance_indicator, get_decomposition, get_visualization
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2
import time
import gensim
import matplotlib.pyplot as plt
from pymoo.visualization.scatter import Scatter
import plot_likert

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

def save_bondora_backlog():
	dataset = pd.read_csv('./thesis-api/dataset/bondora/tasks.csv', encoding='utf-8')
 
	dataset = dataset.loc[dataset["priority.name"].notna()]
 
	dataset = pp.preprocess(dataset)

	backlog = h.get_backlog_issues(dataset)
 
	result = backlog[["summary", "permalink_url"]]
 
	result.to_csv('./thesis-api/dataset/bondora/backlog.csv', encoding='utf-8', index = False)
 
def get_best_task_index(F):
	weights = np.array([1/3, 1/3, 1/3])
    
	decomp = get_decomposition("asf")
 
	I = decomp.do(F, weights).argmin()
	return I
 
def save_bondora_results():
	dataset = pd.read_csv('./thesis-api/dataset/bondora/tasks.csv', encoding='utf-8')
 
	dataset = dataset.loc[dataset["priority.name"].notna()]
	dataset = pp.preprocess(dataset)

	project = "BONDORA"
 
	project_df = dataset

	lda_start_time = time.time()

	done = h.get_done_issues(project_df)

	backlog = h.get_backlog_issues(project_df)
 
	print(len(backlog.index))
 
	number_of_topics, alpha, beta = h.get_hyperparameters("BONDORA")

	lda_model, dictionary = lda.get_lda_model(done, number_of_topics, alpha, beta)

	# lda_model.save("./thesis-api/dataset/Alpha_lda")

	# dictionary.save("./thesis-api/dataset/Alpha_dict")

	# dictionary = gensim.corpora.Dictionary.load("./thesis-api/dataset/Alpha_dict")

	# lda_model = gensim.models.LdaMulticore.load("./thesis-api/dataset/Alpha_lda")
	
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
		if user not in ["Mihkel Põldoja", "Henri Vasserman", "Janek Kossinski", "Kaarel Roben", "Saul Talve"]:
			continue

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
  
		index = get_best_task_index(res.F)
  
		tasks = h.get_individuals_by_bit_array(backlog, res.X[index].astype(np.int))
		print(results)
		break
  
		# tasks[["summary", "permalink_url"]].to_csv("./thesis-api/dataset/bondora/generated/" + user + '.csv', index = False)
  
	# pd.DataFrame(results).to_csv('./thesis-api/dataset/bondora/' + project.lower() + '_validation.csv', index=False)
 
def get_from_backlog_based_on_links(backlog, link_series):

	picked_links_list = link_series.to_numpy().flatten()

	res = backlog[backlog["permalink_url"].isin(picked_links_list)]

	return res
 
def compare_answers_to_gen():
	dataset = pd.read_csv('./thesis-api/dataset/bondora/tasks.csv', encoding='utf-8')

	dataset = dataset.loc[dataset["priority.name"].notna()]
 
	dataset = pp.preprocess(dataset)

	project_df = dataset

	done = h.get_done_issues(project_df)

	backlog = h.get_backlog_issues(project_df)
 
	number_of_topics, alpha, beta = h.get_hyperparameters("BONDORA")

	# lda_model, dictionary = lda.get_lda_model(done, number_of_topics, alpha, beta)

	# lda_model.save("./thesis-api/dataset/Alpha_lda")

	# dictionary.save("./thesis-api/dataset/Alpha_dict")

	dictionary = gensim.corpora.Dictionary.load("./thesis-api/dataset/Alpha_dict")

	lda_model = gensim.models.LdaMulticore.load("./thesis-api/dataset/Alpha_lda")
	
	backlog = lda.add_topic_vector_to_baclog_issues(backlog, lda_model, dictionary, number_of_topics)

	results = {
		'user': [],
		'picked_distance_from_pf': [],
		}

	grouped_users = done.groupby("assignee.name")

	for user, user_df in grouped_users: 
		if user not in ["Mihkel Põldoja", "Henri Vasserman", "Janek Kossinski", "Kaarel Roben", "Saul Talve"]:
			continue

		print(user)
  
		velocity = h.get_velocity(user_df)

		user_backlog = backlog

		user_experience_vector = lda.get_user_experience_topic_vector(user_df, lda_model, dictionary, number_of_topics)
  
		user_backlog["issue_similarity"] = user_backlog.apply(lambda x: h.cosine_similarity_with_intersection(user_experience_vector, x["vector"]), axis = 1)
	
		user_backlog["novelty"] = user_backlog.apply(lambda x: h.calculate_novelty(user_experience_vector, x["vector"]), axis = 1)

		vector = lda.get_user_experience_topic_vector(user_df, lda_model, dictionary, number_of_topics)

		res = get_optimization_result(backlog, vector, velocity)
  
		picked_links = pd.read_csv("./thesis-api/dataset/bondora/answers/" + user + ".csv")
  
		picked_issues = get_from_backlog_based_on_links(user_backlog, picked_links["permalink_url"])
	
		# generated = pd.read_csv("./thesis-api/dataset/bondora/generated/" + user + ".csv")
		# generated_issues = get_from_backlog_based_on_links(user_backlog, generated["permalink_url"])
  
		# print("picked", picked_issues[["summary", "novelty", "issue_similarity", "businessvalue"]].head())
		# print("generated", generated_issues[["summary", "novelty", "issue_similarity", "businessvalue"]].head())
		
		picked_F = np.array([-picked_issues["businessvalue"].sum(), -picked_issues["issue_similarity"].sum(), -picked_issues["novelty"].sum()])
		# generated_F = np.array([-generated_issues["issue_similarity"].sum(), -generated_issues["businessvalue"].sum(), -generated_issues["novelty"].sum()])

		indicator = get_performance_indicator("gd", res.F)

		distance =  indicator.do(picked_F)
  
		best_index = get_best_task_index(res.F)

		results['user'].append(user)
  
		results['picked_distance_from_pf'].append(distance)
  
		pf_without_best = np.delete(res.F, best_index, axis=0)
  
		print(res.F)
		print(pf_without_best)
  
		plot = Scatter()
		plot.add(pf_without_best, s=40, color="blue", label="Individual in PF")
		plot.add(picked_F, s=40, color="red", label="Picked")
		plot.add(res.F[best_index], s=40, color="green", label="Best (also in PF)")
		plot.legend = True
		# plot.save("./thesis-api/dataset/bondora/pf_plots/" + user)
  
	# pd.DataFrame(results).to_csv('./thesis-api/dataset/bondora/picked_distance_from_pf.csv', index=False)

def likert_plots():
	data = pd.DataFrame({
	'How much do you like to work on issue reports that are new to you (issues reports that are related to a topic you haven''t worked on or seen before)?': {
		'1': '3', 
		'2': '2', 
		'3': '5', 
		'4': '3', 
		'5': '2'},
	'How much do you like to work on issue reports related to topics that you have experience with?': {
		'1': '4', 
		'2': '3', 
		'3': '5',
		'4': '5',
		'5': '5'},
	'How much do you like to work on on issue reports that are priority for the business value?': {
		'1': '4', 
		'2': '2', 
		'3': '5',
		'4': '5',
		'5': '3'}})
	data2 = pd.DataFrame({
	'How much would these issue reports increase the business value of the product increment?': {
		'1': '4', 
		'2': '1', 
		'3': '3',
		'4': '3',
		'5': '3'},
	'How much experience do you have with the topics of these issue reports?': {
		'1': '5', 
		'2': '4', 
		'3': '5',
		'4': '3',
		'5': '1'},
	'To what extent do these issues contain topics that are novel to you?': {
		'1': '4', 
		'2': '2', 
		'3': '3',
		'4': '3',
		'5': '5'},
	'How happy would you be with the assigned issue reports?': {
		'1': '5', 
		'2': '3', 
		'3': '5',
		'4': '3',
		'5': '3'},
	})

	ax1 = plot_likert.plot_likert(data, plot_likert.scales.raw5, plot_percentage=True, figsize=(8, 4))
	ax2 = plot_likert.plot_likert(data2, plot_likert.scales.raw5, plot_percentage=True, figsize=(8, 5))


	ax1.figure.tight_layout()
	ax2.figure.tight_layout()

	ax1.figure.savefig('./thesis-api/dataset/bondora/likert_plots/section1.png')
	ax2.figure.savefig('./thesis-api/dataset/bondora/likert_plots/section3.png')

if __name__ == '__main__':
	save_bondora_results()
	# save_bondora_backlog()
	# compare_answers_to_gen()
	# likert_plots()
 