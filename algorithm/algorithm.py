import pandas as pd
import preprocessing as pp
import lda as lda
import nsga2 as nsga2
import numpy as np
import other_helpers as h

def optimize_for_users(backlog, users_df, project):

	# myfile = open('xyz.csv', 'w')

	for _, user in users_df.iterrows():

		user_experience_vector = user['vector']

		backlog["issue_similarity"] = backlog.apply(lambda x: h.cosine_similarity(user_experience_vector, x["vector"]), axis = 1)

		res = nsga2.get_optimization_result(backlog["storypoints"].to_numpy(), backlog["businessvalue_normalized"].to_numpy(), backlog["issue_similarity"].to_numpy(), 15)

		best_solution_indices = res.X.astype(np.int)

		best_solution = h.get_individuals_by_bit_array(backlog, best_solution_indices[0])

		best_solution[["storypoints", "businessvalue_normalized"]].to_csv("result_example.csv")

		print("items selected count: ", len(best_solution))
		print("Best solution found: %s" % res.X.astype(int))
		print("Best solution values: ")
		print(best_solution[["storypoints", "businessvalue"]].head())
		print("storypoints sum: ", best_solution["storypoints"].sum())
		print("businessvalue sum: ", best_solution["businessvalue"].sum())
		print("issue_similarity sum: ", best_solution["issue_similarity"].sum())
		print("Function value: %s" % res.F)
		print("Constraint violation: %s" % res.CV)

		# myfile.writelines(user["assignee.name"] + "," + str(res.F) + "," + project)
		# only for first user for now
		break

	# myfile.close()

if __name__ == '__main__':

	dataset = pd.read_csv('./dataset/jiradataset_issues_v1.4.csv', encoding='utf-8')

	dataset = pp.preprocess(dataset)

	grouped = dataset.groupby("project")

	for project, df in grouped:

		done = h.get_done_issues(df)

		backlog = h.get_backlog_issues(df)

		number_of_topics = 5

		lda_model, dictionary = lda.get_lda_model(done, number_of_topics)

		# print topics
		# for idx, topic in lda_model.print_topics(-1):
			# print('Topic: {} \nWords: {}'.format(idx, topic))

		backlog = lda.add_topic_vector_to_baclog_issues(backlog, lda_model, dictionary, number_of_topics)

		users_df = lda.add_experience_topic_vector_to_users(done, lda_model, dictionary, number_of_topics)

		optimize_for_users(backlog, users_df, project)

		break






