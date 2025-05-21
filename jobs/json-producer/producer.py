from kafka import KafkaProducer
import json
import time
import os

# Get config from environment
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC_NAME = os.getenv('TOPIC_NAME', 'topic_raw')
DATA_PATH = '/data/test_data_amazon.json'

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def produce_data():
    with open(DATA_PATH, 'r') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                producer.send(TOPIC_NAME, value=record)
                print(f"Sent: {record['asin']}")
                time.sleep(0.5)  # Adjust speed here
            except json.JSONDecodeError:
                print("Skipping invalid JSON line")
    
    producer.flush()
    print("Finished sending data")

if __name__ == '__main__':
    produce_data()