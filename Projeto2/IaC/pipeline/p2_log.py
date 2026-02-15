import os
import datetime
import sys

def grava_log(texto, bucket_obj, nome_arquivo_log):
    """
    Grava log no console (para o CloudWatch) e tenta salvar no S3.
    """
    # Define diretório temporário local (seguro em qualquer nó worker)
    import tempfile
    dir_temp = tempfile.gettempdir()
    path_local = os.path.join(dir_temp, nome_arquivo_log)

    # Prepara timestamp
    agora = datetime.datetime.now()
    data_hora = agora.strftime('%Y-%m-%d %H:%M:%S')
    mensagem = f"[{data_hora}] - {texto}\n"

    # 1. Print no console (Stdout) é essencial no EMR
    print(f"--- LOG: {texto}")

    # 2. Persistência no S3 (Append simulado)
    try:
        # Escreve/Anexa no arquivo local temporário
        with open(path_local, "a") as arquivo:
            arquivo.write(mensagem)
        
        # Faz upload para S3 (logs/nome_arquivo)
        if bucket_obj:
            bucket_obj.upload_file(path_local, f"logs/{nome_arquivo_log}")
            
    except Exception as e:
        print(f"ALERTA (p2_jobs): Não foi possível salvar log no S3: {str(e)}")

def salvar_dataframe_s3(df, full_s3_path):
    """
    Salva DataFrame Spark direto no S3 em formato Parquet.
    """
    print(f"--- Salvando dados em: {full_s3_path}")
    df.write.mode("overwrite").partitionBy("label").parquet(full_s3_path)

def salvar_modelo_s3(model, full_s3_path):
    """
    Salva Modelo ML direto no S3.
    """
    print(f"--- Salvando modelo em: {full_s3_path}")
    model.write().overwrite().save(full_s3_path)