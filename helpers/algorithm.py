import pandas as pd
import preprocessing as pp
import lda as lda
import nsga2 as nsga2
import numpy as np
import other_helpers as h

if __name__ == '__main__':

	dataset = pd.read_csv('./dataset/jiradataset_issues_v1.4.csv', encoding='utf-8')

	dataset = dataset.loc[dataset["project"] == "xd"]

	dataset = pp.preprocess(dataset)

	done = pp.get_done_issues(dataset)

	backlog = pp.get_backlog_issues(dataset)

	number_of_topics = 10

	lda_model, dictionary = lda.get_lda_model(done, number_of_topics)

	# print topics
	# for idx, topic in lda_model.print_topics(-1):
	# 	print('Topic: {} \nWords: {}'.format(idx, topic))

	backlog = lda.add_topic_vector_to_baclog_issues(backlog, lda_model, dictionary, number_of_topics)

	backlog = backlog.iloc[:10]

	print(backlog[["storypoints", "businessvalue"]].head(10))
	
	user_df = lda.add_experience_topic_vector_to_users(done, lda_model, dictionary, number_of_topics)

	res = nsga2.get_optimization_result(backlog, 5)

	best_solution_indices =  res.X.astype(int)

	best_solution = h.get_individuals_by_bit_array(backlog, best_solution_indices)

	print("Best solution indices: ", best_solution_indices)
	print("Best solution: ", best_solution.head())
	print("Some important variable: ", -res.F)
	print("Is valid solution: ", res.pf)
