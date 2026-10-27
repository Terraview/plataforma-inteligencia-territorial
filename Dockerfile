FROM apache/airflow:2.10.0

# Muda para root para instalar o Java no sistema operativo do container
USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        default-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Define a variável de ambiente JAVA_HOME essencial para o PySpark funcionar
ENV JAVA_HOME=/usr/lib/jvm/default-java

# Retorna para o utilizador padrão do Airflow
USER airflow

# Copia e instala as dependências do requirements.txt (PySpark, py7zr, python-dotenv, etc.)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt