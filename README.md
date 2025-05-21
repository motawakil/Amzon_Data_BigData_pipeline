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
