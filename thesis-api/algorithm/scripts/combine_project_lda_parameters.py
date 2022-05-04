import pandas as pd
import glob

def bondora():
	df = pd.read_csv('./thesis-api/algorithm/lda_tuning_results/bondora_lda_tuning_results.csv', index_col=None, header=0)

	index = df['Coherence'].idxmax()

	row = df.iloc[index]
 
	print(row)
 
def combine_lda_params():
	dataset = pd.read_csv('./thesis-api/dataset/jiradataset_issues_v1.4.csv', encoding='utf-8')

	projects = dataset.groupby("project")

	result = pd.DataFrame(columns=['project', 'topics', 'alpha', 'beta'])

	for project, _ in projects: 
     
		df = pd.read_csv('./thesis-api/algorithm/lda_tuning_results/' + project.lower() + '_' + 'lda_tuning_results.csv', index_col=None, header=0)
  
		index = df['Coherence'].idxmax()

		row = df.iloc[index]
  
		row["project"] = project.lower()
  
		result = result.append({'project' :project.lower(), 'topics': row["Topics"], 'alpha': row["Alpha"], 'beta': row["Beta"], 'coherence': row['Coherence']}, ignore_index=True)

	result["beta"] = result["beta"].applymap(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)

	result.to_csv('./thesis-api/algorithm/lda_tuning_results/lda_params.csv', index=False)
 


if __name__ == '__main__':
	bondora()
	