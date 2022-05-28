import algorithm.helpers.lda as lda
import algorithm.helpers.nsga2 as nsga2
import numpy as np
import algorithm.helpers.other_helpers as h
import gensim

from pymoo.factory import get_decomposition


def get_best_task_index(F):
	weights = np.array([1/3, 1/3, 1/3])
    
	decomp = get_decomposition("asf")
 
	I = decomp.do(F, weights).argmin()
	return I

def optimize(backlog, user_experience_vector, velocity):

	backlog["issue_similarity"] = backlog.apply(lambda x: h.cosine_similarity_with_intersection(user_experience_vector, x["vector"]), axis = 1)
 
	backlog["novelty"] = backlog.apply(lambda x: h.calculate_novelty(user_experience_vector, x["vector"]), axis = 1)
 
	businessvalue_array = backlog["businessvalue"].to_numpy()
  
	issue_similarity_array = backlog["issue_similarity"].to_numpy()
 
	novelty_array = backlog["novelty"].to_numpy()
 
	problem = nsga2.get_problem(businessvalue_array, issue_similarity_array, novelty_array, velocity)

	res = nsga2.get_optimization_result(problem)
 
	solutions = res.X.astype(np.int)
 
	best_solution_index = get_best_task_index(res.F)

	best_solution = h.get_individuals_by_bit_array(backlog, solutions[best_solution_index])
 
	return best_solution, res.F[best_solution_index]

def generate_solution_for_user(project, dataset, issues_done_by_user, storypoints):
 
	backlog = h.get_backlog_issues(dataset)
 
	number_of_topics, _, _ = h.get_hyperparameters(project)
 
	dictionary = gensim.corpora.Dictionary.load("./algorithm/lda_dicts/" + project)

	lda_model = gensim.models.LdaMulticore.load("./algorithm/lda_models/" + project)	
 
	backlog = lda.add_topic_vector_to_baclog_issues(backlog, lda_model, dictionary, number_of_topics)
 
	vector = lda.get_user_experience_topic_vector(issues_done_by_user, lda_model, dictionary, number_of_topics)
 
	return optimize(backlog, vector, storypoints)

def get_velocity_for_user(project, username, dataset):
 
	return h.get_velocity_for_user(project, username, dataset)