from pyspark.sql import SparkSession, functions as F
from pyspark.sql import DataFrame
import configparser

class MyHelpers:

    def get_spark_session(self, session_params: dict) -> SparkSession:
        spark_session = SparkSession.builder \
        .appName(session_params.get("appName")) \
        .master(session_params.get("master")) \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.10") \
        .config("spark.executor.memory", session_params.get("executor_memory")) \
        .config("spark.executor.cores", session_params.get("executor_cores")) \
        .config("spark.executor.instances", session_params.get("executor_instances")) \
        .getOrCreate()

        return spark_session

    def get_data(self, spark_session: SparkSession, read_params: dict) -> DataFrame:
        input_df = spark_session.read \
        .format(read_params.get("format")) \
        .option("header", read_params.get("header")) \
        .option("sep", read_params.get("sep")) \
        .option("inferSchema", read_params.get("inferSchema")) \
        .load(read_params.get("path"))

        return input_df

    def format_dates(self, date_cols: list, input_df: DataFrame) -> DataFrame:
        ## Make timestamp of string dates/ts
        for column_name in date_cols:
            input_df = input_df.withColumn(column_name, 
            F.date_format(F.col(column_name), "yyyy-MM-dd HH:mm:ss"))

        for column_name in date_cols:
            input_df = input_df.withColumn(column_name, 
            F.to_timestamp(F.col(column_name), "yyyy-MM-dd HH:mm:ss"))
        return input_df

    def make_nulls_to_unknown(self, input_df: DataFrame) -> DataFrame:
        ## Replace Null/None/Empty values with Unknown in string columns        
        string_columns = [field.name for field in input_df.schema.fields if field.dataType.typeName() == 'string']
        for col_name in string_columns:
            input_df = input_df.withColumn(
                col_name, F.when(
                    (F.col(col_name).isNull()) |
                    (F.col(col_name) == "") |
                    (F.lower(F.col(col_name)) == "none") |
                    (F.lower(F.col(col_name)) == "null") |
                    (F.lower(F.col(col_name)) == "empty"), "Unknown"                    
                ).otherwise(F.col(col_name))
            )
        return input_df

    def trim_str_cols(self, input_df) -> DataFrame:
        ## trim all string cols
        string_columns = [field.name for field in input_df.schema.fields if field.dataType.typeName() == 'string']
        for col_name in string_columns:
            input_df = input_df.withColumn(col_name,
             F.trim(F.col(col_name)))

        return input_df

    def write_to_postgresql(self, input_df: DataFrame):    
        config = configparser.RawConfigParser()
        config.read('/home/train/week7/spark/examples/Homework#8/db_conn')
        user_name = config.get('DB', 'user_name')
        password = config.get('DB', 'password')    
        # write to postgresql traindb database cars_cleaned table
        input_df.write.format("jdbc") \
        .option("url", "jdbc:postgresql://localhost:5432/traindb") \
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", "public.cars_cleaned") \
        .option("user", user_name) \
        .option("password", password) \
        .mode("overwrite") \
        .save()