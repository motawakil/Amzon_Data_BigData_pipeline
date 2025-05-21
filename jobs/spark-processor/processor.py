from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, concat_ws, lit, trim, from_json, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# 1. Initialisation de la session Spark
spark = SparkSession.builder \
    .appName("ReviewCleanerStreamingJob") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Schéma des messages JSON attendus depuis Kafka
schema = StructType([
    StructField("reviewerID", StringType(), True),
    StructField("asin", StringType(), True),
    StructField("reviewerName", StringType(), True),
    StructField("reviewText", StringType(), True),
    StructField("overall", IntegerType(), True),
    StructField("summary", StringType(), True),
    StructField("unixReviewTime", IntegerType(), True),
    StructField("reviewTime", StringType(), True),
    StructField("label", IntegerType(), True)  # facultatif
])

# 3. Lecture des messages du topic Kafka `topic_raw`
raw_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "topic_raw") \
    .option("startingOffsets", "latest") \
    .load()

# 4. Parsing JSON du champ `value`
parsed_df = raw_df.selectExpr("CAST(value AS STRING) AS json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*")

# 5. Nettoyage et concaténation
cleaned_df = parsed_df.withColumn("text_prepared",
    concat_ws(" ",
        when(col("summary").isNull(), "").otherwise(col("summary")),
        when(col("reviewText").isNull(), "").otherwise(col("reviewText"))
    )
).withColumn("text_prepared",
    when((col("text_prepared").isNull()) | (trim(col("text_prepared")) == ""), lit("empty_review"))
    .otherwise(col("text_prepared"))
)

# 6. Ajouter la colonne "text_prepared" nettoyée à l'entrée complète
enriched_df = parsed_df.withColumn("text_prepared",
    concat_ws(" ",
        when(col("summary").isNull(), "").otherwise(col("summary")),
        when(col("reviewText").isNull(), "").otherwise(col("reviewText"))
    )
).withColumn("text_prepared",
    when((col("text_prepared").isNull()) | (trim(col("text_prepared")) == ""), lit("empty_review"))
    .otherwise(col("text_prepared"))
)

# 7. Convertir toutes les colonnes (y compris text) en JSON
json_output_df = enriched_df.select(to_json(struct("*")).alias("value"))


# 8. Écriture dans le topic Kafka `topic_processing`
query = json_output_df.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "topic_processing") \
    .option("checkpointLocation", "/tmp/checkpoints/reviews_cleaning") \
    .outputMode("append") \
    .start()

query.awaitTermination()
