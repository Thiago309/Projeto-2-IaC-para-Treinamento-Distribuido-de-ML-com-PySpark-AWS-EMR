# Projeto 2 - Deploy do Stack de Treinamento Distribuído de Machine Learning com PySpark no Amazon EMR
# Script Principal

# Instala pacote Python dentro de código Python
import subprocess
comando = "pip install boto3"
subprocess.run(comando.split())

# Imports
import os
import boto3
import traceback
import pyspark 
from pyspark.sql import SparkSession
from p2_log import grava_log
from p2_processamento import limpa_transforma_dados
from p2_ml import cria_modelos_ml


print("\nLog - Inicializando o Processamento.")

# Cria um recurso de acesso ao S3 via código Python
s3_client = boto3.client('s3', 
                         aws_access_key_id=AWSACCESSKEYID,
                         aws_secret_access_key=AWSSECRETKEY)

# Lista os buckets do S3 para executar o projeto
resposta = s3_client.list_buckets()
for bucket in resposta['Buckets']:
    if bucket['Name'].startswith('p2-pipeline-ML'):
        NOME_BUCKET = bucket['Name']
        break

# Define o objeto de acesso ao bucket via Python
bucket = s3_client.Bucket(NOME_BUCKET)

# Grava o log
grava_log("Log - Bucket Encontrado.", bucket)

# Grava o log
grava_log("Log - Inicializando o Apache Spark.", bucket)

# Cria a Spark Session e grava o log no caso de erro
try:
	spark = SparkSession.builder.appName("Projeto2").getOrCreate()
	spark.sparkContext.setLogLevel("ERROR")
except:
	grava_log("Log - Ocorreu uma falha na Inicialização do Spark", bucket)
	grava_log(traceback.format_exc(), bucket)
	raise Exception(traceback.format_exc())

# Grava o log
grava_log("Log - Spark Inicializado.", bucket)

# Define o ambiente de execução do Amazon EMR
ambiente_execucao_EMR = False if os.path.isdir('dados/') else True

# Bloco de limpeza e transformação
try:
	DadosHTFfeaturized, DadosTFIDFfeaturized, DadosW2Vfeaturized = limpa_transforma_dados(spark, 
																							  bucket, 
																							  NOME_BUCKET, 
																							  ambiente_execucao_EMR)
except:
	grava_log("Log - Ocorreu uma falha na limpeza e transformação dos dados", bucket)
	grava_log(traceback.format_exc(), bucket)
	spark.stop()
	raise Exception(traceback.format_exc())

# Bloco de criação dos modelos de Machine Learning
try:
	cria_modelos_ml (spark, 
					     DadosHTFfeaturized, 
					     DadosTFIDFfeaturized, 
					     DadosW2Vfeaturized, 
					     bucket, 
					     NOME_BUCKET, 
					     ambiente_execucao_EMR)
except:
	grava_log("Log - Ocorreu Alguma Falha ao Criar os Modelos de Machine Learning", bucket)
	grava_log(traceback.format_exc(), bucket)
	spark.stop()
	raise Exception(traceback.format_exc())

# Grava o log
grava_log("Log - Modelos Criados e Salvos no S3.", bucket)

# Grava o log
grava_log("Log - Processamento Finalizado com Sucesso.", bucket)

# Finaliza o Spark (encerra o cluster EMR)
spark.stop()