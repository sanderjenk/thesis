from flask import Flask, request
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

dataset = pd.read_csv('./dataset/jiradataset_issues_v1.4.csv', encoding='utf-8')

dataset = dataset.loc[dataset["project"] == "xd"]

dataset = dataset.iloc[:200]

dataset = pp.preprocess(dataset)

db.issues.delete_many({})

db.issues.insert_many(dataset.to_dict(orient="records"))

@app.route('/api/issues')
def issues():
    
    cursor = db.issues.find({})

    json_docs = [json.dumps(doc, default=json_util.default) for doc in cursor]

    return json.dumps(json_docs, default=json_util.default)


@app.route('/api/generate', methods=['POST'])
def generate():
    issues = []
    
    cursor = db.issues.find({})
    
    [issues.append(doc) for doc in cursor]
    
    df = pd.DataFrame.from_dict(issues)

    user_issues = df.loc[df['key'].isin(request.json)]

    solution = alg.generate_solution_for_user(df, user_issues)
    
    res = solution.to_dict(orient="records")
    
    cursor = db.issues.find({'key': {'$in': solution["key"].to_numpy().tolist()}})
    
    json_docs = [json.dumps(doc, default=json_util.default) for doc in cursor]

    # plug in the algorithm

    return json.dumps(json_docs, default=json_util.default)