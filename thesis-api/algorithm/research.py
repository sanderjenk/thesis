from operator import ge
import pandas as pd
import helpers.lda as lda
import helpers.nsga2 as nsga2
from helpers.terminator import HVTermination
import numpy as np
import helpers.other_helpers as h
from ast import literal_eval
from pymoo.factory import get_crossover, get_mutation, get_sampling, get_performance_indicator
from pymoo.factory import get_crossover, get_mutation, get_sampling
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2
import tqdm
import glob

pd.options.mode.chained_assignment = None  # default='warn'


def get_generations():
    gens = {
		"apstud": 110,
		"COMPASS": 180,
		"DATACASS": 50,
		"dnn": 160,
		"FAB": 225,
		"IS": 190,
		"mesos": 130,
		"MOBILE": 225,
		"mule": 125,
		"nexus": 100,
		"STL": 250,
		"timob": 100,
		"tistud": 175,
		"xd": 300,
	}
    
    return gens


def get_hypervolume(backlog, user_experience_vector, storypoints, generations):

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

	res = minimize(problem,
		algorithm, HVTermination(),
		verbose=False,
  		save_history=True)
 
	hv_indicator = get_performance_indicator("hv", ref_point=np.array([1.1, 1.1, 1.1]))
 
	return hv_indicator.do(res.F)
	
def save_results():
	dataset = pd.read_csv('./thesis-api/dataset/preprocessed_dataset.csv', encoding='utf-8')

	dataset["preprocessed_text"] = dataset["preprocessed_text"].apply(literal_eval)

	grouped_projects = dataset.groupby("project")

	for project, project_df in grouped_projects: 
		
		if (project == "MDL"):
			continue
		

		print(project)
		
		done = h.get_done_issues(project_df)

		backlog = h.get_backlog_issues(project_df)

		grouped_users = project_df.groupby("assignee.name")

		number_of_topics, alpha, beta = h.get_hyperparameters(project)

		lda_model, dictionary = lda.get_lda_model(done, number_of_topics, alpha, beta)
		
		backlog = lda.add_topic_vector_to_baclog_issues(backlog, lda_model, dictionary, number_of_topics)
  
		generations = get_generations().get(project)

		results = {
			'project': [],
			'assignee': [],
			'hypervolume': [],
			}

		pbar = tqdm.tqdm(len(grouped_users))

		for user, user_df in grouped_users: 
		
			if (len(user_df.index) < 1):
				continue

			vector = lda.get_user_experience_topic_vector(user_df, lda_model, dictionary, number_of_topics)

			hypervolume = get_hypervolume(backlog, vector, 15, generations)

			results['project'].append(project)
			results['assignee'].append(user)
			results['hypervolume'].append(hypervolume)
			pbar.update(1)

						
		pd.DataFrame(results).to_csv('./thesis-api/algorithm/validation/' + project.lower() + '.csv', index=False)

def combine_validation():
		
	df_list = [pd.read_csv(filename) for filename in glob.glob("./thesis-api/algorithm/validation/*.csv")]
	
	df = pd.concat(df_list, axis=0)
 
	grouped = df.groupby("project")["hypervolume"].mean()
 
	pd.DataFrame(grouped).to_csv('./thesis-api/algorithm/validation/mean_project_hv.csv')
    
  
if __name__ == '__main__':
	save_results()
	# combine_validation()
	pass