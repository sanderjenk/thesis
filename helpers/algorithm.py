import pandas as pd
import preprocessing as pp
import lda as lda
import nsgaii as nsgaii

if __name__ == '__main__':

	dataset = pd.read_csv('./dataset/jiradataset_issues_v1.4.csv', encoding='utf-8')

	dataset = dataset.loc[dataset["project"] == "xd"]

	dataset = pp.preprocess(dataset)

	done = pp.get_done_issues(dataset)

	backlog = pp.get_backlog_issues(dataset)

	number_of_topics = 10

	# lda_model, dictionary = lda.get_lda_model(done, number_of_topics)

	# for idx, topic in lda_model.print_topics(-1):
	# 	print('Topic: {} \nWords: {}'.format(idx, topic))

	# backlog = lda.add_topic_vector_to_baclog_issues(backlog, lda_model, dictionary, number_of_topics)
	
	# user_df = lda.add_experience_topic_vector_to_users(done, lda_model, dictionary, number_of_topics)

	solution = nsgaii.get_optimal_solution(backlog, 9)