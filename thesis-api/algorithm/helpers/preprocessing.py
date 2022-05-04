from helpers import prioritymapper as pm
from helpers import lda
import numpy as np
import pandas as pd
import datetime
def add_backlog_completed_flag(df):
	done_resolutions = ["Done", "Fixed", "Complete", "Resolved", "Implemented"]

	backlog_statuses = ["Open", "To Do", "New", "Backlog", "To Develop", "Ready for Work"]

	df["backlog"]= df.apply(lambda x: (x["status.name"] in backlog_statuses), axis = 1)

	# df["backlog"]= df.apply(lambda x: ((pd.isna(x["assignee.name"])) &(x["status.name"] in backlog_statuses)), axis = 1)
 
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
    
	df = df[["created", "assignee.name", "priority_normalized", "status.name",	"text", "storypoints", "project", "resolutiondate", "description", "summary", "key"]]

	return df

def add_businessvalue(df):
    
	df["priority"]= df.apply(lambda x: pm.mapPriority(x["project"], x["priority.name"]), axis = 1)

	min = df["priority"].min()

	max = df["priority"].max()

	df["businessvalue"] = df.apply(lambda x: normalize(x["priority"], min, max), axis = 1)

	return df

def normalize(value, min, max):
    
    return (value - min) / (max - min)

def remove_outliers(df, col):
    
	df = df[np.abs(df[col]-df[col].mean()) <= (df[col].std())]
 
	return df

def parse_resolution_date(df):

	df["parsed_resolutiondate"] = df.apply(lambda x: datetime.datetime.strptime(x["resolutiondate"], '%Y-%m-%dT%H:%M:%S.%f%z'), axis = 1)

	return df

def preprocess(df):
	nr_of_issues = len(df.index)
 
	print("starting nr of issues", nr_of_issues)
 
	df = project_tolower(df)
 
	print("add_backlog_completed_flag")

	df = add_backlog_completed_flag(df)
 
	nr_of_issues2 = len(df.index)

	print("after backlog and done filtering", nr_of_issues2)
 
	print("removed", nr_of_issues - nr_of_issues2)

	print("add_businessvalue")

	df = add_businessvalue(df)

	print("merge_desc_sum")

	df = merge_desc_sum(df)

	print("add_preprocessed_text")
 
	df = lda.add_preprocessed_text(df)

	return df
