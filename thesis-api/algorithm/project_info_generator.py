import pandas as pd

if __name__ == '__main__':
	issues = pd.read_csv('./dataset/jiradataset_issues_v1.4.csv', encoding='utf-8')

	projects = issues.groupby("project")
	
	project_names = []
 
	for project, _ in projects: 
     
		project_names.append(project.upper())
  
	projects = pd.read_csv("./dataset/JIRA project list.csv", delimiter=";")

	projects = projects[projects['Project Key'].isin(project_names)]
 
	projects = projects[["Project Key", "Description", "Jira URL", "Git URL" ,"Programing language", "Purpose", "Reference", "Developer"]]
 
	projects.columns = projects.columns.str.replace(' ', '_')
 
	projects.columns = projects.columns.str.lower()
 
	pd.DataFrame(projects).to_csv('./dataset/project_info.csv', index=False)
