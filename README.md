# 🚀 BigDataProject — Real-Time Amazon Review Processing Pipeline

This project is a real-time data processing pipeline designed to ingest, clean, analyze, and visualize Amazon reviews using modern Big Data tools including **Kafka**, **Spark**, **MongoDB**, and **Flask**.


---

## 🧩 Description

This pipeline:
- Preprocesses raw Amazon review data
- Sends the cleaned data into Kafka topics
- Applies real-time classification using Apache Spark
- Stores the results into MongoDB
- Visualizes the classification stats in a Flask dashboard

---

## ✅ Setup Instructions

### 📌 Step 1: Preprocess the Data

```bash
# Create and activate a virtual environment
cd BIGDATAPROJECT
python -m venv venv_processing_data
venv_processing_data\Scripts\activate  # On Windows

# Install required packages
pip install pandas scikit-learn

# Run the script
python processing_data.py
```


### 📌 Step 2: Build and Launch the Pipeline
```bash
docker-compose up -d --build
```

### 📌 Step 3: Build and Launch the Pipeline

####  Once containers are running:
```bash
docker exec -it kafka bash
```
# Inside the Kafka container, run:
```bash
kafka-topics.sh --create --topic topic_raw --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1

kafka-topics.sh --create --topic topic_processing --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1

kafka-topics.sh --create --topic topic_results_training --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1

```


### 📌 Step 4: Monitor Kafka Topics (Optional)
```bash
#### Terminal 1
docker exec -it kafka /opt/bitnami/kafka/bin/kafka-console-consumer.sh \
--bootstrap-server localhost:9092 --topic topic_raw --from-beginning

#### Terminal 2
docker exec -it kafka /opt/bitnami/kafka/bin/kafka-console-consumer.sh \
--bootstrap-server localhost:9092 --topic topic_processing --from-beginning

#### Terminal 3
docker exec -it kafka /opt/bitnami/kafka/bin/kafka-console-consumer.sh \
--bootstrap-server localhost:9092 --topic topic_results_training --from-beginning
```

### 📌 Step 5: Launch the Flask Dashboard
```bash
cd Mongo_visualisation_Bigdata

#### Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

#### Install dependencies
pip install flask pymongo

#### Run the app
flask run

```
