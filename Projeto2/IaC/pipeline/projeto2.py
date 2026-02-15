import sys
import os
import boto3
import datetime
import traceback
from pyspark.sql import SparkSession

# Imports dos módulos:
from p2_log import grava_log
from p2_processamento import limpa_transforma_dados
from p2_ml import cria_modelos_ml

def main():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"log_execucao_{timestamp}.txt"
    
    # Usar o print (que vai para o stdout/logs do controlador do EMR). Só usamos grava_log depois que a variável bucket_obj estiver criada com sucesso.
    print(">>> INICIANDO ORQUESTRADOR (MAIN) <<<")
    
    # Debug: Imprime qual Python está rodando e onde ele está procurando libs
    print(f"--- DEBUG PYTHON EXECUTABLE: {sys.executable}")
    print(f"--- DEBUG SYSPATH: {sys.path}")
    print(f"--- DEBUG ENV PYSPARK_PYTHON: {os.environ.get('PYSPARK_PYTHON', 'Não definido')}")

    nome_bucket = None

    # 1. Tenta pegar o nome do bucket via argumento (O jeito certo via Terraform).
    if len(sys.argv) > 1:
        nome_bucket = sys.argv[1]

        print(f"Nome do bucket recebido via argumento: {nome_bucket}")

    # 2. Fallback: Se não vier argumento, tenta a lógica antiga de descoberta
    else:
        print("Aviso: Nenhum argumento recebido. Tentando descoberta automática...")

        s3_resource_temp = boto3.resource('s3') # Recurso temporário apenas para busca
        
        # Realiza a leitura dos Buckets S3 existentes e me retorna o que desejo utilizar no pipeline.
        for bucket in s3_resource_temp.buckets.all():
            if bucket.name.startswith('bucket-ml-pipeline-123456789'): 
                nome_bucket = bucket.name
                break

    # 3. Validação Final
    if not nome_bucket:
        print("ERRO CRÍTICO: Nome do bucket não definido nem via argumento nem via busca.")
        sys.exit(1)

    # 4. Agora sim, instanciamos o recurso e o objeto do bucket

    bucket_obj = None # Inicializa variável

    try:
        # O Boto3 pega a região automaticamente a do ambiente (us-east-2)
        s3_resource = boto3.resource('s3') 
        bucket_obj = s3_resource.Bucket(nome_bucket)

        print(f"Objeto Bucket instanciado: {bucket_obj.name}")
        grava_log(f"Início da execução. Bucket: {nome_bucket}", bucket_obj, log_file)

    except Exception as e:
        print(f"Erro ao instanciar objeto S3: {str(e)}")
        sys.exit(1)

    try:
        spark = SparkSession.builder \
            .appName("Projeto2_Pipeline_ML") \
            .getOrCreate()
        
        spark.sparkContext.addPyFile("/home/hadoop/pipeline/p2_log.py")
        spark.sparkContext.addPyFile("/home/hadoop/pipeline/p2_processamento.py")
        spark.sparkContext.addPyFile("/home/hadoop/pipeline/p2_ml.py")

        spark.sparkContext.setLogLevel("ERROR")
        
        grava_log("Spark Inicializado com Sucesso.", bucket_obj, log_file)

        # Chama os módulos
        # Nota: Certifique-se que bucket_obj é serializável ou passe apenas nome_bucket se der erro de Pickle

        HTF, TFIDF, W2V = limpa_transforma_dados(spark, bucket_obj, nome_bucket, log_file)
        cria_modelos_ml(spark, HTF, TFIDF, W2V, bucket_obj, nome_bucket, log_file)

        grava_log("PIPELINE FINALIZADO COM SUCESSO.", bucket_obj, log_file)

    except Exception as e:
        erro_formatado = traceback.format_exc()
        mensagem_erro = f"FALHA FATAL NO PIPELINE: {str(e)}\n{erro_formatado}"

        # Tenta gravar no S3 se o bucket estiver disponível
        if bucket_obj:
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