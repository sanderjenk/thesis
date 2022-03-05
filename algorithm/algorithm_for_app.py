import pandas as pd
import helpers.preprocessing as pp
import helpers.lda as lda
import helpers.nsga2 as nsga2
import numpy as np
import helpers.other_helpers as h

def get_best_solution_for_user(backlog, user_experience_vector):

	backlog["issue_similarity"] = backlog.apply(lambda x: h.cosine_similarity(user_experience_vector, x["vector"]), axis = 1)

	res = nsga2.get_optimization_result(backlog["storypoints"].to_numpy(), backlog["businessvalue_normalized"].to_numpy(), backlog["issue_similarity"].to_numpy(), 15)

	best_solution_indices = res.X.astype(np.int)

	best_solution = h.get_individuals_by_bit_array(backlog, best_solution_indices[0])
 
	return best_solution

def generate_solution_for_user(dataset, issues_done_by_user):
 
	done = h.get_done_issues(dataset)

	backlog = h.get_backlog_issues(dataset)
 
	number_of_topics = 5

	lda_model, dictionary = lda.get_lda_model(done, number_of_topics)
	
	backlog = lda.add_topic_vector_to_baclog_issues(backlog, lda_model, dictionary, number_of_topics)
 
	vector = lda.get_user_experience_topic_vector(issues_done_by_user, lda_model, dictionary, number_of_topics)
 
	return get_best_solution_for_user(backlog, vector)


if __name__ == '__main__':
    
	dataset = pd.read_csv('./dataset/jiradataset_issues_v1.4.csv', encoding='utf-8')

	dataset = dataset.loc[dataset["project"] == "xd"]

	issues_done_by_user = dataset.iloc[:10]
 
	dataset = pp.preprocess(dataset)
 
	issues_done_by_user = pp.preprocess(issues_done_by_user)

	solution = generate_solution_for_user(dataset, issues_done_by_user)

	print(solution["storypoints"].sum())