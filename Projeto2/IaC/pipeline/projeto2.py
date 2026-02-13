# Nome do arquivo: main.py
import sys
import boto3
import datetime
import traceback
from pyspark.sql import SparkSession

# IMPORTS CORRIGIDOS AQUI:
from p2_log import grava_log
from p2_processamento import limpa_transforma_dados
from p2_ml import cria_modelos_ml

def main():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"log_execucao_{timestamp}.txt"
    
    print(">>> INICIANDO ORQUESTRADOR (MAIN) <<<")

    s3_resource = boto3.resource('s3', region_name='us-east-2')
    bucket_obj = None
    nome_bucket = None

    try:
        print("Detectando bucket automaticamente...")
        for bucket in s3_resource.buckets.all():
            if bucket.name.startswith('bucket-ml-pipeline'): 
                nome_bucket = bucket.name
                break
        
        if not nome_bucket:
            raise Exception("Nenhum bucket iniciado com 'bucket-ml-pipeline' encontrado.")

        bucket_obj = s3_resource.Bucket(nome_bucket)
        print(f"Bucket Definido: {nome_bucket}")

    except Exception as e:
        print(f"ERRO CRÍTICO NA CONFIGURAÇÃO DO BUCKET: {str(e)}")
        sys.exit(1)

    grava_log("Inicializando Spark Session...", bucket_obj, log_file)

    try:
        spark = SparkSession.builder \
            .appName("Projeto2_Pipeline_ML") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("ERROR")
        
        grava_log("Spark Inicializado com Sucesso.", bucket_obj, log_file)

        # Chama os módulos
        HTF, TFIDF, W2V = limpa_transforma_dados(spark, bucket_obj, nome_bucket, log_file)
        cria_modelos_ml(spark, HTF, TFIDF, W2V, bucket_obj, nome_bucket, log_file)

        grava_log("PIPELINE FINALIZADO COM SUCESSO.", bucket_obj, log_file)

    except Exception as e:
        erro_formatado = traceback.format_exc()
        mensagem_erro = f"FALHA FATAL NO PIPELINE: {str(e)}\n{erro_formatado}"
        grava_log(mensagem_erro, bucket_obj, log_file)
        print(mensagem_erro)
        
        if 'spark' in locals():
            spark.stop()
        sys.exit(1)

    finally:
        if 'spark' in locals():
            spark.stop()

if __name__ == "__main__":
    main()