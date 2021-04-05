from src.etl import extract, transform, load
import json
import csv
import boto3
from src.db.core import connection

# Function to read from csv file
def execute(event, context):

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    s3_resource = boto3.resource("s3")
    s3_object = s3_resource.Object(bucket, key)

    raw = s3_object.get()["Body"].read().decode("utf-8").splitlines()

    df = extract(raw)
    data = transform(df)
    conn = connection()
    load(data, conn)
    conn.close()