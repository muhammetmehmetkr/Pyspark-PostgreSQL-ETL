# Week 8 Homework — Fill-in-the-Blanks: PySpark ETL to PostgreSQL

## Objective

Complete the empty methods in `utility/my_helpers.py` so that `main.py` runs end-to-end:
read a CSV of used-car classifieds, clean it with PySpark, and write the result
into PostgreSQL as `traindb.public.cars_cleaned`.

You will practice:

- Building a `SparkSession` from a parameter dictionary
- Reading CSV with options driven by a parameter dictionary
- Casting/normalizing timestamp columns
- Replacing nulls and empty/`"None"` strings with `"Unknown"`
- Trimming whitespace from all string columns
- Writing a Spark DataFrame to PostgreSQL via JDBC

---

## Dataset

- **File:** `all_anonymized_2015_11_2017_03.csv`
- **Source:** [personal-cars-classifieds.zip](https://github.com/erkansirin78/datasets/raw/master/personal-cars-classifieds.zip)
- **Local path used by `main.py`:** `file:///opt/examples/datasets/all_anonymized_2015_11_2017_03.csv`

Download and unzip the archive, then place the CSV at the path above (or change
`read_params_dict["path"]` in `main.py` to wherever you stored it).

The CSV holds anonymized classified-ad listings for used cars. Two columns are
timestamps stored as strings: `date_created` and `date_last_seen`.

---

## Project structure

```
homework/
├── homework_explanation.md      # this file
├── main.py                      # driver — DO NOT modify the call sequence
└── utility/
    ├── __init__.py
    └── my_helpers.py            # <-- fill in the empty methods here
```

`main.py` instantiates `MyHelpers` and calls each method in order. Your job is to
make every method return the right DataFrame (or perform the right side effect
for `write_to_postgresql`).

> **Note:** `main.py` as shipped imports `my_helpers_answer`. Before you submit,
> change the import to `from utility.my_helpers import MyHelpers` so your
> implementation is exercised.

---

## Prerequisites

1. **PySpark** installed and on `PYTHONPATH`.
2. **PostgreSQL JDBC driver** available to Spark. Either:
   - drop `postgresql-<version>.jar` into `$SPARK_HOME/jars/`, **or**
   - add `--packages org.postgresql:postgresql:42.7.3` (or similar) to your
     `spark-submit` command, **or**
   - add `.config("spark.jars", "/path/to/postgresql.jar")` to the SparkSession
     builder.
3. **Reachable PostgreSQL** instance with database `traindb`.

Default connection settings expected by your `write_to_postgresql` method:

| Property | Value |
|---|---|
| URL | `jdbc:postgresql://<host>:5432/traindb` |
| Driver | `org.postgresql.Driver` |
| Table | `public.cars_cleaned` |
| User / Password | as provided in your environment |
| Mode | `overwrite` |

(Hard-code these inside `write_to_postgresql`, or read them from environment
variables — your call.)

---

## Tasks (method by method)

### 1. `get_spark_session(session_params: dict) -> SparkSession`

Build and return a `SparkSession` configured from `session_params`. Required keys:

- `master`, `appName`
- `executor_memory`, `executor_cores`, `executor_instances`

Use `SparkSession.builder` with `.master(...)`, `.appName(...)`, and the three
executor configs via `.config("spark.executor.<x>", ...)`. Finish with
`.getOrCreate()`.

### 2. `get_data(spark_session, read_params: dict) -> DataFrame`

Read the CSV using values from `read_params` (`format`, `header`, `sep`,
`inferSchema`, `path`). Return the DataFrame.

### 3. `format_dates(date_cols: list, input_df: DataFrame) -> DataFrame`

For each column in `date_cols`, convert the raw string into a proper
`timestamp`. The source values look like:

```
2016-09-22 16:14:43.439290+00
```

Hint: parse with `F.to_timestamp(col, "yyyy-MM-dd HH:mm:ss.SSSSSSx")`, optionally
re-format to `"yyyy-MM-dd HH:mm:ss"` for a clean output, then cast back to
timestamp. Loop over `date_cols` and return the transformed DataFrame.

### 4. `make_nulls_to_unknown(input_df: DataFrame) -> DataFrame`

For every **string** column, replace `NULL` and the literal string `"None"` with
`"Unknown"`. Use `df.dtypes` to discover string columns dynamically — do not
hard-code column names.

### 5. `trim_str_cols(input_df) -> DataFrame`

Apply `F.trim` to every string column. Again, discover string columns
dynamically.

### 6. `write_to_postgresql(input_df: DataFrame)`

Write the DataFrame to `traindb.public.cars_cleaned` via JDBC in `overwrite`
mode. Sketch:

```python
input_df.write.format("jdbc") \
    .option("url", "jdbc:postgresql://<host>:5432/traindb") \
    .option("driver", "org.postgresql.Driver") \
    .option("dbtable", "public.cars_cleaned") \
    .option("user", "<user>") \
    .option("password", "<password>") \
    .mode("overwrite") \
    .save()
```

---

## How to run

```bash
cd 03_pyspark/spark_homework/week8_fill_blanks/homework
spark-submit \
  --packages org.postgresql:postgresql:42.7.3 \
  main.py
```

You should see, in order:

1. Raw schema + first 5 rows
2. `format dates` — `date_created` and `date_last_seen` printed as `timestamp`
3. `make_nulls_to_unknown` — no `null` and no `"None"` literals in string columns
4. `trim_str_cols` — no leading/trailing whitespace
5. `postgresql` — write completes without error

---

## Validation

After the job finishes, connect to PostgreSQL and check:

```sql
\c traindb
SELECT COUNT(*) FROM public.cars_cleaned;
SELECT * FROM public.cars_cleaned LIMIT 5;
\d public.cars_cleaned
```

Expectations:

- Row count matches the input CSV (minus header).
- `date_created` and `date_last_seen` are `timestamp` columns.
- No `NULL` values in string columns; no rows where a string column equals
  `"None"`.
- No string values with leading/trailing spaces.

---

## Submission

Submit:

1. Your completed `utility/my_helpers.py`.
2. `main.py` (with the import switched to `utility.my_helpers`).
3. A screenshot or short text dump of `SELECT * FROM public.cars_cleaned LIMIT 5;`
   proving the table was written.

> Do **not** submit `my_helpers_answer.py` or modify `main.py`'s call order.