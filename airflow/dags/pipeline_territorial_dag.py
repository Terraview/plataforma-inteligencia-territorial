from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="pipeline_inteligencia_territorial",
    default_args=default_args,
    description="Pipeline completa: Bronze (IBGE/CAGED) -> Prata (Spark) -> Ouro (Esquema Estrela)",
    schedule_interval=None,  

    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,      

    tags=["territorio", "spark", "caged", "ibge"],
) as dag:

    #  CAMADA BRONZE 
    
    t_bronze_ipca = BashOperator(
        task_id="bronze_ibge_ipca",
        bash_command="export PYTHONPATH=$PYTHONPATH:/opt/airflow && python -m src.bronze.ibge_ipca",
    )

    t_bronze_pib = BashOperator(
        task_id="bronze_ibge_pib",
        bash_command="export PYTHONPATH=$PYTHONPATH:/opt/airflow && python -m src.bronze.ibge_pib",
    )

    t_bronze_populacao = BashOperator(
        task_id="bronze_ibge_population",
        bash_command="export PYTHONPATH=$PYTHONPATH:/opt/airflow && python -m src.bronze.ibge_population",
    )

    t_bronze_caged = BashOperator(
        task_id="bronze_caged_ftp",
        bash_command="export PYTHONPATH=$PYTHONPATH:/opt/airflow && python -c 'from src.bronze.caged import download_caged_ftp; download_caged_ftp()'",
        cwd="/opt/airflow",
    )

    #  CAMADA SILVER 

    t_prata_extraction_7z = BashOperator(
        task_id="prata_extract_7z",
        bash_command="export PYTHONPATH=$PYTHONPATH:/opt/airflow && python -m src.prata.convesion",
    )

    t_prata_caged_2019 = BashOperator(
        task_id="prata_caged_2019",
        bash_command="export PYTHONPATH=$PYTHONPATH:/opt/airflow && python -m src.prata.caged_silver_2019",
        cwd="/opt/airflow",
    )

    t_prata_caged_2020_2023 = BashOperator(
        task_id="prata_caged_2020_2023",
        bash_command="export PYTHONPATH=$PYTHONPATH:/opt/airflow && python /opt/airflow/src/prata/caged_silver_2020-2023.py",
        cwd="/opt/airflow",
    )

    t_prata_caged_to_json = BashOperator(
        task_id="prata_caged_parquet_to_json",
        bash_command="export PYTHONPATH=$PYTHONPATH:/opt/airflow && python -m src.prata.caged_parquet_to_json",
    )

    #  CAMADA GOLD

    t_gold_star_schema = BashOperator(
        task_id="gold_build_star_schema",
        bash_command="export PYTHONPATH=$PYTHONPATH:/opt/airflow && python -m src.gold.build_star_schema --write --show",
        cwd="/opt/airflow",
    )

    t_gold_load_postgres = BashOperator(
        task_id="gold_load_postgres",
        bash_command="export PYTHONPATH=$PYTHONPATH:/opt/airflow && python -m src.gold.load_postgres",
        cwd="/opt/airflow",
    )

    #  ORQUESTRAÇÃO DAS DEPENDÊNCIAS 

    # 1. As extrações Bronze correm em paralelo
    [t_bronze_ipca, t_bronze_pib, t_bronze_populacao, t_bronze_caged]

    # 2. Fluxo do CAGED (Download -> Extração 7z -> Silver 2019 & 2020-2023 -> Consolidação JSON)
    t_bronze_caged >> t_prata_extraction_7z >> [t_prata_caged_2019, t_prata_caged_2020_2023]
    [t_prata_caged_2019, t_prata_caged_2020_2023] >> t_prata_caged_to_json

    # 3. Convergência para a camada Gold (Exige o JSON CAGED consolidado e os dados IBGE da Bronze)
    [t_prata_caged_to_json, t_bronze_ipca, t_bronze_pib, t_bronze_populacao] >> t_gold_star_schema
    t_gold_star_schema >> t_gold_load_postgres