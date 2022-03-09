import pandas as pd
import numpy as np
from scipy import spatial

def get_done_issues(df):

	df = df.loc[(df["assignee.name"].notna()) & (df["resolutiondate"].notna())]

	return df

def get_backlog_issues(df):

	df = df.loc[(df["assignee.name"].isna()) & (df["resolutiondate"].isna())]

	return df

def get_individuals_by_bit_array(df, bit_array):

    indices = np.array(bit_array == 1)

    return df.iloc[indices]

def cosine_similarity(vector1, vector2):

    return 1 - spatial.distance.cosine(vector1, vector2)

def get_hyperparameters(project):
    
    df = pd.read_csv('./algorithm/lda_tuning_results/' + project + '_lda_tuning_results.csv', encoding='utf-8')

    index = df['Coherence'].idxmax()

    row = df.iloc[index]

    topics = row["Topics"]

    alpha = row["Alpha"]

    try:
        alpha = float(alpha)
    except ValueError:
        print("Alpha is string")

    beta = row["Beta"]

    try:
        beta = float(beta)
        
    except ValueError:
        print("Beta is string")

    return topics, alpha, beta


