from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable

# Function that will be executed by the PythonOperator
def check_variable():
    my_var = Variable.get("my_variable", default_var=1)
    if int(my_var) == 2:
        raise ValueError("Variable is set to 2, failing the task.")
    elif int(my_var) == 1:
        print("Variable is set to 1, task succeeds.")
    else:
        print("Variable is not set to 1 or 2.")

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

# Define the DAG
dag = DAG(
    'variable_check_dag',
    default_args=default_args,
    description='A simple DAG to check a variable',
    schedule_interval=None,
)

# Define the PythonOperator
task = PythonOperator(
    task_id='check_variable_task',
    python_callable=check_variable,
    dag=dag,
)

# Set the task in the DAG
task
