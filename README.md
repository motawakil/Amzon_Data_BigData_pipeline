# 🚀 BigDataProject — Real-Time Amazon Review Processing Pipeline

This project is a real-time data processing pipeline designed to ingest, clean, analyze, and visualize Amazon reviews using modern Big Data tools including **Kafka**, **Spark**, **MongoDB**, and **Flask**.

---

## 📁 Project Structure

BIGDATAPROJECT/
├── data/
│ ├── mongo/
│ ├── test_data_amazon.json
│ ├── train_data.json
│ └── validation_data.json
│
├── jobs/
│ ├── json-producer/
│ │ ├── dockerfile
│ │ ├── producer.py
│ │ ├── requirements.txt
│ │ └── test_data_amazon.json
│ │
│ ├── mongo-writer/
│ │ ├── dockerfile
│ │ ├── mongo_writer.py
│ │ └── requirements.txt
│ │
│ ├── spark-inference/
│ │ ├── model/
│ │ ├── dockerfile
│ │ ├── inference.py
│ │ └── requirements.txt
│ │
│ └── spark-processor/
│ ├── Dockerfile
│ └── processor.py
│
├── Mongo_visualisation_Bigdata/
│ ├── pycache/
│ ├── static/
│ │ └── js/
│ │ └── charts.js
│ ├── templates/
│ │ └── charts.html
│ ├── venv/
│ ├── app.py
│ └── requirements.txt
│
├── Trained_Models/
│ ├── Logistic Regression Model.ipynb
│ ├── Naive Bayes Model.ipynb
│ └── Random Forest Model.ipynb
│
├── venv_processing_data/
├── Data.json
├── Docker-compose.yaml
└── processing_data.py
