# Connections management demo repository

This repository contains the DAG code used in the [Manage Astro connections in branch-based deploy workflows](https://deploy-preview-3125--gallant-neumann-56599d.netlify.app/astro/astro-use-case/use-case-astro-connections) use case.

The DAGs in this repository use the following packages:

- [Common SQL Airflow provider](https://registry.astronomer.io/providers/apache-airflow-providers-common-sql/versions/latest).
- [Amazon Airflow provider](https://registry.astronomer.io/providers/apache-airflow-providers-amazon/versions/latest).
- [Snowflake Airflow provider](https://registry.astronomer.io/providers/apache-airflow-providers-snowflake/versions/latest).

## How to use this repository from scratch

To use this repository, you will need:

- The [Astro CLI](https://docs.astronomer.io/astro/cli/overview).
- An [Astro account](https://www.astronomer.io/try-astro/) with two [Astro Deployments](https://docs.astronomer.io/astro/create-deployment), one for development (`Dev`) and one for production (`Prod`).
- An account in a SQL-based data warehouse with two distinct databases: one for development, one for production data, each containing an empty schema called `COOKIES`. This example uses a Snowflake account for which a [30-day free trial](https://trial.snowflake.com/?owner=SPN-PID-365384) is available.
- An [AWS account](https://aws.amazon.com/). A [free tier](https://aws.amazon.com/free/) is available and sufficient for this project.

Follow the steps in the [Manage Astro connections in branch-based deploy workflows](https://deploy-preview-3125--gallant-neumann-56599d.netlify.app/astro/astro-use-case/use-case-astro-connections) use case to set up the connections and branch-based deployment workflow for your Astro account.

## Demo script 

This demo is running in CE Astrophysics. To demo connections management, you can use the following script:

- Explain branch-based deployments as a CI/CD best practice. In this case there is a dev (`conn-management-demo-dev`) and prod (`conn-management-demo-prod`) deployment. 
- Both deployments are connected to this GitHub repository with automated brach based deploy using our [template](https://docs.astronomer.io/astro/ci-cd-templates/github-actions): 
    - On every push to the `dev` branch, the `conn-management-demo-dev` deployment is updated.
    - On every merged pull request to the `main` branch, the `conn-management-demo-prod` deployment is updated.
- An AWS (`aws_conn_management_demo`) and a Snowflake connection (`snowflake_conn_management_demo`) is needed in both deployments. The demo DAG reads information (about Swiss Christmas cookies 🍪) from a file in S3 and writes it to a Snowflake table.
- Without Astro connections management you would have to set up the connections in both deployments manually. This is tedious and can lead to errors.
- With the new Astro connections management feature, you can set up the connections once in a helpful form and use them in multiple deployments in the workspace.
- Show the Snowflake connection (`snowflake_conn_management_demo`) in the Environment tab of the CE Astrophysics workspace:
    - The Snowflake connection should be available to all Deployments in the workspace by default (for example a spontaneous deployment a developer creates to test a new feature). This is why this connection is set to `Linked to all`. By default the dev database in Snowflake `CONN_DEMO_DEV` is used.
    - For the production deployment `conn-management-demo-prod` the database field is overwritten to `CONN_DEMO_PROD`.
- Show the AWS connection (`aws_conn_management_demo`) in the Environment tab of the CE Astrophysics workspace:
    - The AWS connection should only be available to deployments that really need it, this is why it is set to `Restricted` and then was linked to both deployments. No overrides are needed.
- No other setup is needed to run the DAGs successfully in both deployments, creating and populating the `COOKIE_RECIPES` table in Snowflake.
    - The `upload_cookie_recipes` DAG is a helper to run once to upload the cookie recipes to S3 from a local json file.
    - The `collect_cookie_recipes` DAG is the main DAG that reads the cookie recipes from S3, writes them to Snowflake and then runs a query on the Snowflake table to get all recipes with a max baking time below 10 minutes.
    - Point out that it is important to not forget to add the Airflow provider for all connections used in the DAGs in the `requirements.txt` file.
- If there is a need to change the connection, for example to point at a different schema for the production deployment, this can be done without even opening the Airflow UI or changing any DAG code by another override in the connection management form.

To also demo branch-based deploys just make a small comment change in the DAG file and push to `dev` and merge to `main`. Please clean up the comments afterwards :)

## Data sources

The cookie recipes used in this demo are from the following sources:

- Mailänderli: https://cuisinehelvetica.com/2021/11/27/swiss-christmas-cookie-recipe-mailanderli/
- Basler Brunsli: https://cuisinehelvetica.com/2021/12/09/recipe-basler-brunsli/ 
- Spitzbuebe: https://www.newlyswissed.com/recipe-for-swiss-spitzbuebe-cookies/
- Zimtsterne: https://cuisinehelvetica.com/2021/12/17/recipe-zimtsterne/
