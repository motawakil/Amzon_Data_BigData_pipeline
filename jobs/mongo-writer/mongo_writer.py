import os
import json
from kafka import KafkaConsumer
from pymongo import MongoClient
from datetime import datetime
import time
time.sleep(25)  # Attendre que Kafka soit prêt
# Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC_NAME = 'topic_results_training'
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongodb:27017')
DB_NAME = os.getenv('DB_NAME', 'sentiment_analysis')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'predictions')

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Kafka Consumer
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='mongo-writer-group'
)

# Sentiment Mapping
SENTIMENT_MAP = {
    0: 'negative',
    1: 'neutral',
    2: 'positive'
}

def transform_message(message_value):
    """Extract and transform required fields"""
    return {
        'reviewID': message_value.get('reviewerID'),
        'asin': message_value.get('asin'),
        'reviewerName': message_value.get('reviewerName'),
        'text': message_value.get('text'),
        'filtered_words': message_value.get('filtered', []),
        'sentiment': SENTIMENT_MAP.get(message_value.get('prediction', 2), 'unknown'),
        'timestamp': datetime.utcnow()
    }

print("Starting MongoDB Writer...")
for message in consumer:
    try:
        data = transform_message(message.value)
        collection.insert_one(data)
        print(f"Inserted document: {data['reviewID']}")
    except Exception as e:
        print(f"Error processing message: {str(e)}")