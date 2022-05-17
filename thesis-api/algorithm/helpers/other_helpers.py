import pandas as pd
import numpy as np
from scipy import spatial
import datetime
import math

def get_done_issues(df):
    
	df = df.loc[df["done"] == True]
 
	return df

def get_backlog_issues(df):

	df = df.loc[df["backlog"] == True]

	return df

def get_individuals_by_bit_array(df, bit_array):

    indices = np.array(bit_array == 1)

    return df.iloc[indices]

def intersect_vectors(developer_vector, issue_vector):
    
    new_issue_vector = []
    
    new_developer_vector = []
    
    for i in range(len(issue_vector)):
        
        if (issue_vector[i] == 0):
            
            continue
        
        new_issue_vector.append(issue_vector[i])
        
        new_developer_vector.append(developer_vector[i])
                
    return new_developer_vector, new_issue_vector

def cosine_similarity_with_intersection(developer_vector, issue_vector):
    
    developer_vector, issue_vector = intersect_vectors(developer_vector, issue_vector)
    
    return cosine_similarity(developer_vector, issue_vector)

def cosine_similarity(vector1, vector2):

    return 1 - spatial.distance.cosine(vector1, vector2)

def calculate_novelty(developer_vector, issue_vector):
    
    highest_topic_index = np.argmax(issue_vector)
    
    if (developer_vector[highest_topic_index] == 0):
        
        return 1
    
    return 0

def get_hyperparameters(project):
    
    df = pd.read_csv('./algorithm/lda_tuning_results/lda_params.csv', encoding='utf-8')

    row = df.loc[df["project"] == project.lower()].iloc[0]

    topics = row["topics"]

    alpha = row["alpha"]

    try:
        alpha = float(alpha)
    except ValueError:
        pass

    beta = row["beta"]

    try:
        beta = float(beta)
        
    except ValueError:
        pass
    return topics, alpha, beta

def get_velocity(user_issues):
    
    user_issues["parsed_resolutiondate"] = user_issues.apply(lambda x: datetime.datetime.strptime(x["resolutiondate"], '%Y-%m-%dT%H:%M:%S.%f%z'), axis = 1)
    
    user_issues["parsed_resolutiondate"] = pd.to_datetime(user_issues['parsed_resolutiondate'], utc=True)
    
    grouped = user_issues.groupby(pd.Grouper(key="parsed_resolutiondate", freq= "2W", origin="start"))

    issue_counts = []

    for _, df in grouped:
        if (len(df.index) == 0):
            continue
        issue_counts.append(len(df.index))

    return int(math.ceil(np.mean(issue_counts)))

def get_velocity_for_user(project, username, dataset):

    done = get_done_issues(dataset)

    user_issues = done.loc[(done["project"] == project) & (done["assignee.name"] == username) & (done["resolutiondate"].notnull())]

    return get_velocity(user_issues)
	


