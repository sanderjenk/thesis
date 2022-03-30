from helpers import prioritymapper as pm
from helpers import lda
import numpy as np
import pandas as pd

def add_backlog_flag(df):
	done_resolutions = ["Done", "Fixed", "Complete", "Resolved", "Implemented"]

	backlog_statuses = ["Open", "To Do", "New", "Backlog"]

	df["backlog"]= df.apply(lambda x: (x["status.name"] in backlog_statuses), axis = 1)
 
	df["done"] = df.apply(lambda x: ((pd.notna(x["assignee.name"])) & (x["resolution.name"]in done_resolutions)), axis = 1)
 
	df = df.drop(df[(df["backlog"] == False) & (df["done"]== False)].index)

	return df

def project_tolower(df):
    df['project'].str.lower()
    return df

def merge_desc_sum(df):
    
	df['description'] = df['description'].fillna("")
 
	df['summary'] = df['summary'].fillna("")
 
	df["text"] = df["description"] + " " + df["summary"]
 
	return df

def cols(df):
    
	df = df[["created", "assignee.name", "priority", "status.name",	"text", "storypoints", "project", "resolutiondate", "description", "summary", "key", "businessvalue", "businessvalue_normalized"]]

	return df

def fix_storypoints(df):
    
	storypoints_projects = ["xd", "tistud", "timob", "nexus", "mule", "mesos", "dnn", "apstud"]

	df = df.drop(df[(df["storypoints"] == 0) | (df["storypoints"].isna()) & df["project"].isin(storypoints_projects)].index)

	df.loc[~df["project"].isin(storypoints_projects), "storypoints"] = 1
 
	return df

def map_priorities(df):
    
	df["priority"]= df.apply(lambda x: pm.mapPriority(x["project"], x["priority.name"]), axis = 1)
 
	return df

def calculate_business_values(df):
    
	df['businessvalue'] = df['storypoints'] * df['priority']
 
	return df

def normalize_column(df, column_name):
    
	min = df[column_name].min()
 
	max = df[column_name].max()
 
	df[column_name + "_normalized"] = df.apply(lambda x: normalize(x[column_name], min, max), axis = 1)
 
	return df

def normalize(value, min, max):
    
    return (value - min) / (max - min)

def remove_outliers(df, col):
    
	df = df[np.abs(df[col]-df[col].mean()) <= (df[col].std())]
 
	return df

def preprocess(df):
	df = project_tolower(df)
	print("add_backlog_flag")
	df = add_backlog_flag(df)
	print("map_priorities")

	df = map_priorities(df)
	print("fix_storypoints")

	df = fix_storypoints(df)
	print("remove_outliers")

	df = remove_outliers(df, "storypoints")
	print("calculate_business_values")

	df = calculate_business_values(df)
	print("merge_desc_sum")

	df = merge_desc_sum(df)
	print("add_preprocessed_text")

	df = lda.add_preprocessed_text(df)
	print("normalize_column")

	df = normalize_column(df, "businessvalue")

	return df
