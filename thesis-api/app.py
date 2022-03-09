from flask import Flask, request, Response
import pandas as pd
from flask_pymongo import PyMongo
import json
from bson import json_util
from flask_cors import CORS
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

dataset = pd.read_csv('./dataset/jiradataset_issues_xd_v1.4.csv', encoding='utf-8')

dataset = dataset.loc[dataset["project"] == "xd"]

dataset['description'] = dataset['description'].fillna("")

dataset = dataset.iloc[:200]

dataset = pp.preprocess(dataset)

db.issues.delete_many({})

db.issues.insert_many(dataset.to_dict(orient="records"))

@app.route('/api/projects')
def projects():
    projects = pd.read_csv("./dataset/project_info.csv", encoding="utf-8")
    
    projects = projects.to_dict(orient="records")
    
    return get_json(projects)

@app.route('/api/issues')
def issues():
    
    cursor = db.issues.find({})

    return get_json(cursor, True)

@app.route('/api/generate', methods=['POST'])
def generate():
    issues = []
    
    cursor = db.issues.find({})
    
    [issues.append(doc) for doc in cursor]
    
    df = pd.DataFrame.from_dict(issues)

    user_issues = df.loc[df['key'].isin(request.json)]
    
    print(request.json)
    
    print(user_issues.head(5))

    solution = alg.generate_solution_for_user(df, user_issues, 15)
    
    cursor = db.issues.find({'key': {'$in': solution["key"].to_numpy().tolist()}})
    
    return get_json(cursor, True)

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
            doc.pop('assignee.name', None)
            doc.pop('resolutiondate', None)
            doc.pop('resolution.description', None)
            doc.pop('resolution.name', None)
            doc.pop('sprint', None)
        
        json_docs.append(json.dumps(doc, default=json_util.default))
        
    return json.dumps(json_docs, default=json_util.default)
    