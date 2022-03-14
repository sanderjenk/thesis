import pandas as pd
import glob

if __name__ == '__main__':

	dataset = pd.read_csv('../../dataset/jiradataset_issues_v1.4.csv', encoding='utf-8')

	projects = dataset.groupby("project")

	result = pd.DataFrame(columns=['project', 'topics', 'alpha', 'beta'])

	for project, _ in projects: 
     
		df = pd.read_csv('../lda_tuning_results/' + project.lower() + '_' + 'lda_tuning_results.csv', index_col=None, header=0)
  
		index = df['Coherence'].idxmax()

		row = df.iloc[index]
  
		row["project"] = project.lower()
  
		result = result.append({'project' :project.lower(), 'topics': row["Topics"], 'alpha': row["Alpha"], 'beta': row["Beta"]}, ignore_index=True)

	result.to_csv('../lda_tuning_results/lda_params.csv', index=False)