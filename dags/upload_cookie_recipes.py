"""
## Upload Cookie Recipes from a Local File to S3

This DAG uploads cookie recipes from a local file to S3.
"""

from airflow.decorators import dag
from airflow.models.baseoperator import chain
from airflow.providers.amazon.aws.transfers.local_to_s3 import (
    LocalFilesystemToS3Operator,
)
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator
from pendulum import datetime

MY_AWS_CONN = "aws_conn_management_demo"
FILE_PATH = "include/recipes.json"
S3_BUCKET = "ce-conn-management-demo-cookie-jar-dnd"


@dag(
    start_date=datetime(2023, 11, 23),
    schedule=None,
    catchup=False,
    tags=["helper"],
)
def upload_cookie_recipes():
    create_cookie_bucket = S3CreateBucketOperator(
        task_id="create_cookie_bucket",
        bucket_name=S3_BUCKET,
        aws_conn_id=MY_AWS_CONN,
    )

    upload_cookie_recipes = LocalFilesystemToS3Operator(
        task_id="upload_cookie_recipes",
        filename=FILE_PATH,
        dest_key="cookie_recipes.json",
        dest_bucket=S3_BUCKET,
        aws_conn_id=MY_AWS_CONN,
        replace=True,
    )

    chain(create_cookie_bucket, upload_cookie_recipes)


upload_cookie_recipes()
