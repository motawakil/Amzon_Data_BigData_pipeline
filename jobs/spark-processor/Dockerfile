FROM bitnami/spark:3.5

WORKDIR /app

# Switch to root for installations
USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y python3-pip gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Create writable NLTK directory
RUN mkdir -p /usr/share/nltk_data && \
    chmod a+rwx /usr/share/nltk_data

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -m nltk.downloader -d /usr/share/nltk_data punkt wordnet averaged_perceptron_tagger

# Switch back to spark user
USER 1001

COPY processor.py .

CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0", "processor.py"]