from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from bson.json_util import dumps
from flask_cors import CORS
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["sentiment_analysis"]
collection = db["predictions"]

@app.route("/")
def index():
    return render_template("charts.html")

@app.route("/api/sentiment_counts")
def sentiment_counts():
    # Get optional time range filter from request
    days = request.args.get('days', default=None, type=int)
    
    pipeline = []
    
    # Apply time filter if specified
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        pipeline.append({"$match": {"timestamp": {"$gte": cutoff_date}}})
    
    # Group by sentiment
    pipeline.append({"$group": {"_id": "$sentiment", "count": {"$sum": 1}}})
    
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route("/api/sentiment_over_time")
def sentiment_over_time():
    # Get optional time range filter from request
    days = request.args.get('days', default=30, type=int)
    interval = request.args.get('interval', default='day', type=str)
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Define time grouping format based on interval
    time_format = {
        'hour': '%Y-%m-%d-%H',
        'day': '%Y-%m-%d',
        'week': '%Y-%U',
        'month': '%Y-%m'
    }.get(interval, '%Y-%m-%d')
    
    pipeline = [
        {"$match": {"timestamp": {"$gte": cutoff_date}}},
        {"$project": {
            "sentiment": 1,
            "date": {"$dateToString": {"format": time_format, "date": "$timestamp"}}
        }},
        {"$group": {
            "_id": {
                "date": "$date",
                "sentiment": "$sentiment"
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.date": 1}}
    ]
    
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route("/api/recent_reviews")
def recent_reviews():
    # Get optional sentiment filter
    sentiment = request.args.get('sentiment', default=None, type=str)
    limit = request.args.get('limit', default=10, type=int)
    
    # Build query
    query = {}
    if sentiment:
        query["sentiment"] = sentiment
    
    docs = collection.find(query).sort("timestamp", -1).limit(limit)
    return dumps(docs)

@app.route("/api/top_keywords")
def top_keywords():
    # Get optional filters
    sentiment = request.args.get('sentiment', default=None, type=str)
    days = request.args.get('days', default=None, type=int)
    
    pipeline = []
    
    # Apply filters if specified
    match_conditions = {}
    
    if sentiment:
        match_conditions["sentiment"] = sentiment
    
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        match_conditions["timestamp"] = {"$gte": cutoff_date}
    
    if match_conditions:
        pipeline.append({"$match": match_conditions})
    
    # Continue with the aggregation
    pipeline.extend([
        {"$unwind": "$filtered_words"},
        {"$group": {"_id": "$filtered_words", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route("/api/sentiment_by_source")
def sentiment_by_source():
    # Assuming documents have a 'source' field (if not, you'll need to add it to your data)
    pipeline = [
        {"$group": {
            "_id": {
                "source": "$source", 
                "sentiment": "$sentiment"
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route("/api/stats")
def get_stats():
    # Get total document count
    total = collection.count_documents({})
    
    # Get count by sentiment
    sentiment_counts = collection.aggregate([
        {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}}
    ])
    
    # Get average sentiment score (assuming you have a numeric score field)
    # If not, this can be adapted based on your schema
    avg_score = 0
    try:
        avg_result = collection.aggregate([
            {"$group": {"_id": None, "avgScore": {"$avg": "$score"}}}
        ])
        avg_doc = next(avg_result, None)
        if avg_doc:
            avg_score = avg_doc.get('avgScore', 0)
    except:
        # If no score field exists, we'll just return 0
        pass
    
    # Get latest document timestamp
    latest = collection.find_one(sort=[("timestamp", -1)])
    latest_time = latest.get('timestamp') if latest else None
    
    stats = {
        "total": total,
        "sentiment_counts": list(sentiment_counts),
        "avg_score": avg_score,
        "latest_timestamp": latest_time
    }
    
    return dumps(stats)

if __name__ == "__main__":
    app.run(debug=True)