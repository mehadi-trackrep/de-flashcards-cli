FLASHCARDS = [
    # SQL
    {"topic": "sql", "question": "What is a window function in SQL?", "answer": "A window function performs calculations across a set of rows related to the current row without collapsing them like GROUP BY. Examples: ROW_NUMBER(), RANK(), SUM() OVER (PARTITION BY ...)."},
    {"topic": "sql", "question": "What's the difference between INNER JOIN and LEFT JOIN?", "answer": "INNER JOIN returns only matching rows from both tables. LEFT JOIN returns all rows from the left table and matched rows from the right (NULLs if no match)."},
    {"topic": "sql", "question": "What is a CTE (Common Table Expression)?", "answer": "A CTE is a temporary named result set defined with WITH clause. It improves readability and can be referenced multiple times in the same query."},
    {"topic": "sql", "question": "What is the difference between WHERE and HAVING?", "answer": "WHERE filters rows before grouping. HAVING filters groups after GROUP BY is applied. HAVING can reference aggregate functions; WHERE cannot."},
    {"topic": "sql", "question": "What is an index in a database?", "answer": "An index is a data structure that speeds up data retrieval at the cost of extra storage and slower writes. Common types: B-tree, Hash, Bitmap."},

    # Python
    {"topic": "python", "question": "What is a generator in Python?", "answer": "A generator is a function that yields values lazily using 'yield', avoiding loading everything into memory. Useful for processing large datasets."},
    {"topic": "python", "question": "What does df.groupby() do in pandas?", "answer": "It splits a DataFrame into groups based on column values, then you apply aggregation functions like .sum(), .mean(), .count() on each group."},
    {"topic": "python", "question": "What is the difference between map(), filter(), and reduce()?", "answer": "map() applies a function to each element. filter() keeps elements matching a condition. reduce() cumulatively applies a function to produce a single result."},
    {"topic": "python", "question": "What is a context manager in Python?", "answer": "A context manager manages resources with 'with' statement, ensuring setup and teardown happen correctly. Example: with open('file.csv') as f — file is auto-closed."},

    # Pipeline
    {"topic": "pipeline", "question": "What is an ETL pipeline?", "answer": "ETL stands for Extract, Transform, Load. Data is extracted from sources, transformed (cleaned/aggregated), then loaded into a destination like a data warehouse."},
    {"topic": "pipeline", "question": "What is the difference between ETL and ELT?", "answer": "In ETL, transformation happens before loading. In ELT, raw data is loaded first, then transformed inside the destination (e.g., BigQuery, Snowflake). ELT is common in modern cloud data stacks."},
    {"topic": "pipeline", "question": "What is Apache Airflow?", "answer": "Airflow is an open-source workflow orchestration platform. Pipelines are defined as DAGs (Directed Acyclic Graphs) in Python, with scheduling, retries, and monitoring built in."},
    {"topic": "pipeline", "question": "What is idempotency in data pipelines?", "answer": "An idempotent pipeline produces the same result no matter how many times it runs. It's critical for safe retries — re-running doesn't duplicate or corrupt data."},

    # Warehouse
    {"topic": "warehouse", "question": "What is a fact table vs a dimension table?", "answer": "Fact tables store measurable events (sales, clicks) with foreign keys. Dimension tables store descriptive attributes (customer name, product). Together they form a star schema."},
    {"topic": "warehouse", "question": "What is data partitioning?", "answer": "Partitioning splits a large table into smaller physical segments (e.g., by date) to improve query performance and reduce scan costs in systems like BigQuery or Hive."},
    {"topic": "warehouse", "question": "What is a slowly changing dimension (SCD)?", "answer": "SCD tracks how dimension attributes change over time. Type 1 overwrites old data. Type 2 adds a new row with versioning. Type 3 stores old and new values in separate columns."},
    {"topic": "warehouse", "question": "What is dbt (data build tool)?", "answer": "dbt is a transformation framework that lets analysts write SQL SELECT statements as models. It handles dependencies, testing, documentation, and version control for warehouse transformations."},

    # Streaming
    {"topic": "streaming", "question": "What is Apache Kafka?", "answer": "Kafka is a distributed event streaming platform. Producers write messages to topics, consumers read from them. It enables real-time data pipelines and event-driven architectures."},
    {"topic": "streaming", "question": "What is the difference between batch and stream processing?", "answer": "Batch processing handles data in large chunks at scheduled intervals. Stream processing handles data continuously as it arrives in real time (e.g., Kafka, Flink, Spark Streaming)."},
    {"topic": "streaming", "question": "What is exactly-once semantics in streaming?", "answer": "It guarantees each message is processed exactly once — no duplicates, no data loss — even on failures. Achieved via idempotent producers and transactional APIs in systems like Kafka."},

    # Cloud
    {"topic": "cloud", "question": "What is BigQuery and what makes it different?", "answer": "BigQuery is Google Cloud's serverless data warehouse. It uses columnar storage and separates compute from storage, allowing massive parallel SQL queries at petabyte scale with no infrastructure management."},
    {"topic": "cloud", "question": "What is object storage (e.g., S3, GCS)?", "answer": "Object storage stores data as objects (files + metadata) in buckets rather than file hierarchies. It's cheap, durable, and scalable — commonly used as a data lake layer."},
    {"topic": "cloud", "question": "What is the difference between a data lake and a data warehouse?", "answer": "A data lake stores raw, unstructured or semi-structured data cheaply (e.g., S3). A data warehouse stores structured, processed data optimized for analytics (e.g., Snowflake, BigQuery)."},
]

TOPICS = sorted(set(card["topic"] for card in FLASHCARDS))
