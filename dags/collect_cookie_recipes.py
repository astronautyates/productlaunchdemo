"""
## Retrieve cookie recipes from S3 and insert them into Snowflake

This DAG retrieves cookie recipes from S3 and inserts them into Snowflake.
It is a toy DAG to showcase Airflow connections management on Astro.
To run this DAG you need:

- A Snowflake connection named `snowflake_conn_management_demo`
- An AWS connection named `aws_conn_management_demo` with full access to S3
"""

from airflow.decorators import dag, task
from airflow.models.baseoperator import chain
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from pendulum import datetime
import json

MY_AWS_CONN = "aws_conn_management_demo"
MY_DB_CONN = "snowflake_conn_management_demo"
S3_BUCKET = "ce-conn-management-demo-cookie-jar-dnd"
FILE_KEY = "cookie_recipes.json"


@dag(
    start_date=datetime(2023, 11, 23),
    schedule="@daily",
    catchup=False,
    tags=["connections_management"],
    doc_md="""
    ### Example DAG to showcase Airflow connections management on Astro + branch-based deploys
    
    This DAG retrieves cookie recipes from S3 and inserts them into Snowflake.

    The two connections necessary are defined in the Astro UI of the Astrophysics 
    workspace. 

    [GitHub Repo](https://github.com/astronomer/ce-conn-management-demo)
    (the README includes some notes on how to demo the connections management 
    and branch-based deploys features)

    In case of questions please reach out to the DevRel team in 
    [#team_community_and_devrel](https://astronomer.slack.com/archives/C056TA36X4N)
    """,
    description="Demo DAG to showcase Airflow connections management on Astro",
)
def collect_cookie_recipes():
    @task
    def get_cookies_from_s3(aws_conn_id: str, bucket_name: str, key: str):
        "Gets cookie recipes from S3."
        s3_hook = S3Hook(aws_conn_id=aws_conn_id)
        cookie_recipes = s3_hook.read_key(key=key, bucket_name=bucket_name)
        cookie_json = json.loads(cookie_recipes)
        return cookie_json

    cookies_from_s3 = get_cookies_from_s3(
        aws_conn_id=MY_AWS_CONN, bucket_name=S3_BUCKET, key=FILE_KEY
    )

    create_cookie_table_if_not_exists = SQLExecuteQueryOperator(
        task_id="create_cookie_table_if_not_exists",
        conn_id=MY_DB_CONN,
        sql="""
            CREATE TABLE IF NOT EXISTS cookie_recipes (
                cookie_name VARCHAR(50) PRIMARY KEY,
                cookie_ingredients VARCHAR(256),
                cookie_added_ingredients VARCHAR(256),
                baking_time_min_minutes NUMBER(5,2),
                baking_time_max_minutes NUMBER(5,2)
            );
            TRUNCATE TABLE cookie_recipes;
        """,
    )

    @task
    def create_cookie_sql(cookie_recipes):
        "Creates SQL statement to insert cookie recipes."
        cookie_name = cookie_recipes["name"]
        cookie_ingredients = cookie_recipes["ingredients"]
        cookie_added_ingredients = cookie_recipes["added_ingredients"]
        baking_time_min_minutes = cookie_recipes["baking_time_min_minutes"]
        baking_time_max_minutes = cookie_recipes["baking_time_max_minutes"]

        sql = f"""INSERT INTO cookie_recipes 
            VALUES (
            '{cookie_name}',
            '{cookie_ingredients}',
            '{cookie_added_ingredients}',
            {baking_time_min_minutes},
            {baking_time_max_minutes}
            )
        """
        return sql

    get_quick_cookies = SQLExecuteQueryOperator(
        task_id="get_quick_cookies",
        conn_id=MY_DB_CONN,
        sql="""
            SELECT * FROM cookie_recipes 
            WHERE baking_time_max_minutes < 10;
        """,
    )

    @task
    def bake_cookies(cookie_recipe):
        "Print cookie information."
        cookie_name = cookie_recipe[0]
        cookie_ingredients = cookie_recipe[1]
        cookie_added_ingredients = cookie_recipe[2]
        baking_time_min_minutes = cookie_recipe[3]
        baking_time_max_minutes = cookie_recipe[4]

        print(f"Baking {cookie_name} cookies...")
        print(f"Ingredients: {cookie_ingredients}")
        print(f"Added ingredients: {cookie_added_ingredients}")
        print(
            f"Baking time: {baking_time_min_minutes} to {baking_time_max_minutes} minutes"
        )
        print("Done baking cookies!")

    cookie_sql = create_cookie_sql.expand(cookie_recipes=cookies_from_s3)

    insert_cookie_recipe = SQLExecuteQueryOperator.partial(
        task_id="insert_cookie_recipe", conn_id=MY_DB_CONN
    ).expand(sql=cookie_sql)

    chain(
        create_cookie_table_if_not_exists,
        insert_cookie_recipe,
        get_quick_cookies,
        bake_cookies.expand(cookie_recipe=get_quick_cookies.output),
    )


collect_cookie_recipes()
