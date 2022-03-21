import pandas as pd
import helpers.preprocessing as pp
import helpers.lda as lda
import helpers.nsga2 as nsga2
import numpy as np
import helpers.other_helpers as h

def get_best_solution_for_user(backlog, user_experience_vector, storypoints):

	backlog["issue_similarity"] = backlog.apply(lambda x: h.cosine_similarity_with_intersection(user_experience_vector, x["vector"]), axis = 1)
 
	backlog["novelty"] = backlog.apply(lambda x: h.calculate_novelty(user_experience_vector, x["vector"]), axis = 1)
 
	businessvalue_array = backlog["businessvalue_normalized"].to_numpy()
 
	storypoints_array = backlog["storypoints"].to_numpy()
 
	issue_similarity_array = backlog["issue_similarity"].to_numpy()
 
	novelty_array = backlog["novelty"].to_numpy()

	res = nsga2.get_optimization_result(storypoints_array, businessvalue_array, issue_similarity_array, novelty_array, storypoints)

	best_solution_indices = res.X.astype(np.int)

	best_solution = h.get_individuals_by_bit_array(backlog, best_solution_indices[0])
 
	return best_solution

def generate_solution_for_user(project, dataset, issues_done_by_user, storypoints):
 
	done = h.get_done_issues(dataset)

	backlog = h.get_backlog_issues(dataset)
 
	number_of_topics, alpha, beta = h.get_hyperparameters(project)
 
	lda_model, dictionary = lda.get_lda_model(done, number_of_topics, alpha, beta)
	
	backlog = lda.add_topic_vector_to_baclog_issues(backlog, lda_model, dictionary, number_of_topics)
 
	vector = lda.get_user_experience_topic_vector(issues_done_by_user, lda_model, dictionary, number_of_topics)
 
	return get_best_solution_for_user(backlog, vector, storypoints)