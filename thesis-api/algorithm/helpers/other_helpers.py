import pandas as pd
import numpy as np
from scipy import spatial

def get_done_issues(df):
    
	df = df.loc[df["backlog"] == False]
 
	return df

def get_backlog_issues(df):

	df = df.loc[df["backlog"] == True]

	return df

def get_individuals_by_bit_array(df, bit_array):

    indices = np.array(bit_array == 1)

    return df.iloc[indices]

def cosine_similarity(vector1, vector2):

    return 1 - spatial.distance.cosine(vector1, vector2)

def get_hyperparameters(project):
    
    df = pd.read_csv('./algorithm/lda_tuning_results/lda_params.csv', encoding='utf-8')

    row = df.loc[df["project"] == project.lower()].iloc[0]

    topics = row["topics"]

    alpha = row["alpha"]

    try:
        alpha = float(alpha)
    except ValueError:
        print("Alpha is string: " + str(type(alpha)))

    beta = row["beta"]

    try:
        beta = float(beta)
        
    except ValueError:
        print("Beta is string")

    return topics, alpha, beta


