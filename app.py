from flask import Flask, request
import pandas as pd
from flask_pymongo import PyMongo
import json
from bson import json_util
from flask_cors import CORS

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://mongodb:27017/thesis"

CORS(app)

mongo = PyMongo(app)

db = mongo.db

df = pd.read_csv('./dataset/jiradataset_issues_v1.4.csv', encoding='utf-8')

df = df.loc[df["project"] == "xd"].iloc[:300]

df = df[["key", "summary", "description", "priority.name", "storypoints", "project"]]

df['description'] = df['description'].fillna("")

# db.issues.delete_many({})

db.issues.insert_many(df.to_dict(orient="records"))


@app.route('/api/issues')
def issues():
    json_docs = []

    cursor = db.issues.find({})

    json_docs = [json.dumps(doc, default=json_util.default) for doc in cursor]

    return json.dumps(json_docs, default=json_util.default)


@app.route('/api/generate', methods=['POST'])
def generate():
    keys = request.json

    # plug in the algorithm

    return "hello world"
