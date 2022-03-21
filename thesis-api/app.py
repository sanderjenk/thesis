from flask import Flask, request, Response
import pandas as pd
from flask_pymongo import PyMongo
import json
from bson import json_util
from flask_cors import CORS
import numpy as np
import sys
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

# db.issues.delete_many({})

# db.issues.insert_many(dataset.to_dict(orient="records"))

@app.route('/api/projects')
def projects():
    projects = pd.read_csv("./dataset/project_info.csv", encoding="utf-8")
    
    projects = projects.to_dict(orient="records")
    
    return get_json(projects)

@app.route('/api/generate', methods=['POST'])
def generate():
    issues = []
    
    project = request.args["project"]
    
    storypoints = request.args["storypoints"]
    
    username = request.args["username"]
    
    cursor = db.issues.find({"project": {"$eq": project}})    
    
    [issues.append(doc) for doc in cursor]
    
    df = pd.DataFrame.from_dict(issues)

    cursor = db.issues.find({"project": {"$eq": project},'assignee': {'$eq': username}})
    
    user_issues = []
    
    [user_issues.append(doc) for doc in cursor]

    user_issues_df = pd.DataFrame.from_dict(user_issues)
    
    solution = alg.generate_solution_for_user(project, df, user_issues_df, int(storypoints))
    
    cursor = db.issues.find({'key': {'$in': solution["key"].to_numpy().tolist()}})

    return get_json(cursor, True)

@app.route('/api/developers', methods=['GET'])
def developers():
    project = request.args["project"]

    cursor = db.issues.distinct("assignee", {"project": project})
    
    return get_json(cursor, False)

@app.route('/api/feedback', methods=['POST'])
def feedback():
    print(request.json)
    
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
    