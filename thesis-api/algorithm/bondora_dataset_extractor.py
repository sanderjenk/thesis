import asana
import pandas as pd
import glob
import json
import ast
import numpy as np
import math
 
def mapping_method(task_dict):
    return task_dict["gid"]

def get_tasks(client):
	result = client.tasks.get_tasks_for_project('1199093054441620', opt_pretty=True)
	result = list(result)
	task_ids = map(mapping_method, result)
	tasks = []
	for t_id in task_ids:
		task = client.tasks.get_task(str(t_id), opt_pretty=True)
		tasks.append(task)
	pd.DataFrame(tasks).to_csv('./thesis-api/dataset/bondora/Alpha_tasks.csv')

def map_priorites(custom_fields):
	data = ast.literal_eval(custom_fields)
	priority = None
	for item in data:
		if item["name"] == "Priority":
			priority = item["display_value"]
	return priority

def map_assignee(assignee_field):
	if isinstance(assignee_field, float) and math.isnan(assignee_field):
		return None
	data = ast.literal_eval(assignee_field)
	return data["name"]

def create_overview():
	files = glob.glob('./thesis-api/dataset/bondora/tasks/*')
 
	model_results = {
						'Project': [],
						'Total': [],
						'Missing': [],
						'Missing_percent': [],
						'Backlog': [],
						'Bl_Missing': [],
						'Bl_Missing_percent': [],
						'UA_Backlog': [],
						'UA_Bl_Missing': [],
						'UA_Bl_Missing_percent': [],
						}
 
	for file in files:
		df = pd.read_csv(file)
		df["priority"] = df["custom_fields"].apply(lambda x: map_priorites(x))
  
		df["assignee.name"] = df['assignee'].apply(lambda x: map_assignee(x))

		df = df.drop(columns=['assignee_status', 'tags', 'resource_subtype', 'resource_type', 'permalink_url', 'projects', 'followers', 'hearted', 'hearts', 'likes', 'liked', 'num_hearts', 'num_likes', 'memberships', 'workspace', 'custom_fields', 'due_at', 'start_at'])
		df.set_index("gid", inplace=True)
  
		total_count = len(df.index)
		none_count = len(df.loc[df["priority"].isna()])
  
		model_results['Project'].append(file)
		model_results['Total'].append(total_count)
		model_results['Missing'].append(none_count)
		model_results['Missing_percent'].append(none_count/total_count * 100)
  
		df = df.loc[df["completed"] == False]
  
		total_count = len(df.index)
		none_count = len(df.loc[df["priority"].isna()])
  
		model_results['Backlog'].append(total_count)
		model_results['Bl_Missing'].append(none_count)
		model_results['Bl_Missing_percent'].append(none_count/total_count * 100)
  
		df = df.loc[df["assignee.name"].isna()]
  
		model_results['UA_Backlog'].append(total_count)
		model_results['UA_Bl_Missing'].append(none_count)
		model_results['UA_Bl_Missing_percent'].append(none_count/total_count * 100)
  
		print(df.loc[df["assignee.name"].isna()].head(20))
  
	pd.DataFrame(model_results).to_csv('./thesis-api/dataset/bondora/priority_overview.csv')
		
def preprocess_tasks():
	df = pd.read_csv('./thesis-api/dataset/bondora/Alpha_tasks.csv')

	df["priority.name"] = df["custom_fields"].apply(lambda x: map_priorites(x))

	df["assignee.name"] = df['assignee'].apply(lambda x: map_assignee(x))

	df = df.rename(columns={"gid": "key", 'notes': 'description', 'name': 'summary', 'completed_at': 'resolutiondate'})

	df["resolution.name"] = np.where(df["completed"] == True, "Done", "Something")

	df["status.name"] = np.where(df["completed"] == False, "Backlog", "Something")

	df["project"] = "BONDORA"

	df = df.drop(columns=['completed', 'Unnamed: 0', 'start_on', 'parent', 'assignee_status', 'tags', 'resource_subtype', 'resource_type', 'projects', 'followers', 'hearted', 'hearts', 'likes', 'liked', 'num_hearts', 'num_likes', 'memberships', 'workspace', 'custom_fields', 'due_at', 'start_at', 'due_on', 'modified_at'])
	
	df.set_index("key", inplace=True)

	pd.DataFrame(df).to_csv('./thesis-api/dataset/bondora/tasks.csv')
  
if __name__ == '__main__':
	engineers_team_id = "1199884836511725"

	token = '1/1200414016932628:8289d4de612d27dbdaa2109f6d309d5f'
 
	client = asana.Client.access_token(token)

	# get_projects(client, engineers_team_id)
 
	# get_users(client)
 
	get_tasks(client)
 
	preprocess_tasks()
 
 
