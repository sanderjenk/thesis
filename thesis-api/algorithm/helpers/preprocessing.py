from helpers import prioritymapper as pm
import numpy as np
import pandas as pd

def add_backlog_flag(df):
	df["backlog"]= df.apply(lambda x: ((x["assignee"]) == None) & (x["resolutiondate"] == None), axis = 1)
	return df

def merge_desc_sum(df):
	df['description'] = df['description'].fillna("")
	df['summary'] = df['summary'].fillna("")
	df["text"] = df["description"] + " " + df["summary"]
	return df

def cols(df):
	df = df[["created", "assignee", "priority", "status.name",	"text", "storypoints", "project", "resolutiondate", "description", "summary", "key", "businessvalue", "businessvalue_normalized"]]
	return df

def fill_story_points(df):
	df['storypoints'] = df['storypoints'].fillna(1)
	return df

def replace_zero_story_points(df):
	df['storypoints'] = df['storypoints'].replace(0, 1)
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

def replace_nans(df):
	df = df.where(pd.notnull(df), None)
	return df

def rename_assignee(df):
	df = df.rename(columns={"assignee.name": "assignee"})
	return df

def preprocess(df):
	df = rename_assignee(df)
	df = map_priorities(df)
	df = fill_story_points(df)
	# df = replace_zero_story_points(df)
	df = remove_outliers(df, "storypoints")
	df = calculate_business_values(df)
	df = merge_desc_sum(df)
	df = normalize_column(df, "businessvalue")
	df = replace_nans(df)
	df = add_backlog_flag(df)
	# df = cols(df)
	return df
