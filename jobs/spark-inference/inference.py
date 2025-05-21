from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
from pyspark.sql.functions import col, from_json, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# 1. Spark session
spark = SparkSession.builder.appName("ReviewSentimentPredictor").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# 2. Kafka schema
schema = StructType([
    StructField("reviewerID", StringType(), True),
    StructField("asin", StringType(), True),
    StructField("reviewerName", StringType(), True),
    StructField("reviewText", StringType(), True),
    StructField("overall", IntegerType(), True),
    StructField("summary", StringType(), True),
    StructField("unixReviewTime", IntegerType(), True),
    StructField("reviewTime", StringType(), True),
    StructField("text_prepared", StringType(), True)
])

# 3. Load trained ML model
model = PipelineModel.load("model")

# 4. Read from topic_processing
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "topic_processing") \
    .option("startingOffsets", "latest") \
    .load()




parsed_df = kafka_df.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*")
parsed_df = parsed_df.withColumnRenamed("text_prepared", "text")

# 5. Apply model
predicted_df = model.transform(parsed_df)

# 6. Select relevant columns

result_df = predicted_df.select(
    col("reviewerID"),
    col("asin"),
    col("text").alias("text_input"),
    col("prediction").cast("int").alias("predicted_sentiment"),
    to_json(struct("*")).alias("value")
)


# 7. Write to topic_results_training
query = result_df.select("value").writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "topic_results_training") \
    .option("checkpointLocation", "/tmp/checkpoints/inference") \
    .outputMode("append") \
    .start()




query.awaitTermination()
