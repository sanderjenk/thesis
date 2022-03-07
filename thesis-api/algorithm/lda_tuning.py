import tqdm
import gensim
import pandas as pd
import helpers.lda as lda
import pandas as pd
import helpers.preprocessing as pp

if __name__ == '__main__':

	# Read data into df
	dataset = pd.read_csv('../dataset/jiradataset_issues_v1.4.csv', encoding='utf-8')

	dataset = pp.preprocess(dataset)

	topics_range, alpha, beta = lda.get_parameter_lists()

	grouped = dataset.groupby("project")

	for project, df in grouped:
		
		df = df.sample(200)
		
		preprocessed_docs = lda.get_preprocessed_docs(df)

		id2word = lda.get_dictionary(preprocessed_docs) 

		id2word.filter_extremes(no_below=15, no_above=0.7, keep_n=100000)

		corpus = lda.get_bow_corpus(id2word, preprocessed_docs)

		lemmatized_data = preprocessed_docs.values.tolist()

		# Validation sets
		num_of_docs = len(corpus)
		corpus_sets = [gensim.utils.ClippedCorpus(corpus, int(num_of_docs*0.75)), 
					corpus]

		corpus_title = ['75% Corpus', '100% Corpus']

		model_results = {
						'Validation_Set': [],
						'Topics': [],
						'Alpha': [],
						'Beta': [],
						'Coherence': []
						}

		pbar = tqdm.tqdm(total=(len(beta)*len(alpha)*len(topics_range)*len(corpus_title)))
		
		for i in range(len(corpus_sets)):
			
			for k in topics_range:
				
				for a in alpha:
					
					for b in beta:
						
						cv = lda.get_coherence_value(corpus=corpus_sets[i], dictionary=id2word, lemmatized_data=lemmatized_data, 
													k=k, a=a, b=b)
						
						model_results['Validation_Set'].append(corpus_title[i])
						model_results['Topics'].append(k)
						model_results['Alpha'].append(a)
						model_results['Beta'].append(b)
						model_results['Coherence'].append(cv)
						
						pbar.update(1)

		pd.DataFrame(model_results).to_csv('./lda_tuning_results/' + project + '_' + 'lda_tuning_results.csv', index=False)
		pbar.close()