from utility.my_helpers import MyHelpers
from pyspark.sql import SparkSession, functions as F

my_helper_obj = MyHelpers()

## get spark session
session_params_dict = {
    "master": "local[2]",
    "appName": "Clean Transactions",
    "executor_memory": "1500M",
    "executor_cores": "1",
    "executor_instances": "2"
}
spark = my_helper_obj.get_spark_session(session_params_dict)

# read data
read_params_dict = {
    "format": "csv",
    "header": True,
    "sep": ",",
    "inferSchema": True,
    "path": "/home/train/week7/spark/examples/datasets/all_anonymized_2015_11_2017_03.csv"
}

df = my_helper_obj.get_data(spark_session=spark, read_params=read_params_dict)
df.show(n=5, truncate=False)
df.printSchema()

## format dates
df1 = my_helper_obj.format_dates(date_cols=["date_created", "date_last_seen"], input_df=df)
print("---- Format Dates ----")
df1.show(n=5, truncate=False)
df1.printSchema()

## make_nulls_to_unknown
df2 = my_helper_obj.make_nulls_to_unknown(input_df=df1)
print("---- Make nulls to Unknown ----")
df2.show(5)
df2.printSchema()

## trim_str_cols
df3 = my_helper_obj.trim_str_cols(input_df=df2)
print("---- Trim string columns ----")
df3.printSchema()
df3.show(5)

## write_postgresql
print("---- Writed to Postgresql ----")
my_helper_obj.write_to_postgresql(df3)

spark.stop()