from flask import Flask, request, Response
import pandas as pd
from flask_pymongo import PyMongo
import json
from bson import json_util
from flask_cors import CORS
import numpy as np
import sys
from ast import literal_eval

pd.options.mode.chained_assignment = None  # default='warn'

sys.path.insert(0, './algorithm')
sys.path.insert(0, './algorithm/helpers')

import algorithm.algorithm_for_app as alg
import algorithm.helpers.preprocessing as pp

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/thesis"

CORS(app)

mongo = PyMongo(app)

db = mongo.db

# dataset = pd.read_csv('./dataset/jiradataset_issues_v1.4.csv', encoding='utf-8')

# dataset = pp.preprocess(dataset)

# dataset.to_csv('./dataset/preprocessed_dataset.csv')

dataset = pd.read_csv('./dataset/preprocessed_dataset.csv', encoding='utf-8')

dataset["preprocessed_text"] = dataset["preprocessed_text"].apply(literal_eval)


@app.route('/api/projects')
def projects():
    projects = pd.read_csv("./dataset/project_info.csv", encoding="utf-8")
    
    projects = projects.to_dict(orient="records")
    
    return get_json(projects)

@app.route('/api/generate', methods=['POST'])
def generate():
    
    project = request.args["project"]
    
    storypoints = request.args["storypoints"]
    
    username = request.args["username"]
    
    project_issues = dataset.loc[dataset["project"] == project]

    user_issues = project_issues.loc[(project_issues["assignee.name"] == username)]
    
    solution = alg.generate_solution_for_user(project, project_issues, user_issues, int(storypoints))
    
    return solution.to_json(orient="records")

@app.route('/api/developers', methods=['GET'])
def developers():
    project = request.args["project"]
    
    project_issues = dataset.loc[(dataset["project"] == project) & (dataset["assignee.name"].notna())]

    developers = project_issues["assignee.name"].unique()
    
    return Response(json.dumps(developers.tolist()),  mimetype='application/json')

@app.route('/api/velocity', methods=['GET'])
def velocity():
    project = request.args["project"]

    username = request.args["username"]
    
    velocity = alg.get_velocity_for_user(project, username, dataset)
    
    return str(velocity)

@app.route('/api/feedback', methods=['POST'])
def feedback():

    db.feedback.insert_one(request.json)

    return Response(status=201)

def get_json(cursor, issues = False):
    
    json_docs = []
    
    for doc in cursor:
        
        if (issues):
            ## these assholes can be NaN
            doc.pop('assignee', None)
            doc.pop('resolutiondate', None)
            doc.pop('resolution.description', None)
            doc.pop('resolution.name', None)
            doc.pop('sprint', None)
        
        json_docs.append(json.dumps(doc, default=json_util.default))
        
    return json.dumps(json_docs, default=json_util.default)
    