from pyspark.sql.functions import col, lower, regexp_replace, count, when
from pyspark.ml.feature import StringIndexer, RegexTokenizer, StopWordsRemover, HashingTF, IDF, Word2Vec, MinMaxScaler

# Import do módulo de log
from p2_log import grava_log, salvar_dataframe_s3

def calcula_valores_nulos(df):
    
    # Calcula nulos de todas as colunas em uma única ação do Spark.
    expressoes = [count(when(col(c).isNull(), c)).alias(c) for c in df.columns]

    # Otimização: Se o DF for vazio, evita erro de index out of range
    resultado = df.select(expressoes).collect()

    if resultado:
        return resultado[0].asDict()
    
    return {c: 0 for c in df.columns}

def limpa_transforma_dados(spark, bucket_obj, nome_bucket, log_file):
    
    # Garante que não duplique 's3://' se o nome já vier com ele
    bucket_name_clean = nome_bucket.replace("s3://", "")
    base_s3 = f"s3://{bucket_name_clean}"
    
    grava_log("Iniciando Módulo de Processamento...", bucket_obj, log_file)

    try:
        path_csv = f"{base_s3}/dados/dataset.csv"
        grava_log(f"Lendo arquivo: {path_csv}", bucket_obj, log_file)
        
        # 1. Leitura e Redistribuição (CRÍTICO PARA PERFORMANCE NO EMR)
        # O inferSchema=True é importante se houver colunas numéricas além do texto.
        reviews = spark.read.csv(path_csv, header=True, escape="\"", inferSchema=True)
        
        # Reparticiona para garantir que todos os nós do cluster trabalhem.
        # Se o arquivo for pequeno (<1GB), 20 partições é seguro. Se for grande, aumente.
        reviews = reviews.repartition(20) 
        
        # Cache aqui é bom pois vamos usar para contar nulos e depois processar.
        reviews.cache()

        grava_log(f"Total de registros brutos: {reviews.count()}", bucket_obj, log_file)
        
    # Caso não consiga realizar o processamento de leitura do arquivo, retornarar o error.
    except Exception as e:
        grava_log(f"ERRO FATAL ao ler CSV: {str(e)}", bucket_obj, log_file)
        raise e

    # 2. Limpeza de Nulos
    nulos = calcula_valores_nulos(reviews)

    grava_log(f"Contagem de nulos: {nulos}", bucket_obj, log_file)
    
    # Se a quantidade de nulos for maior que zero, realiza a limpeza dos valores nulos.
    if sum(nulos.values()) > 0:
        grava_log("Removendo linhas com valores nulos...", bucket_obj, log_file)
        reviews = reviews.dropna()

    # 3. Processamento de Texto (NLP)
    # Verifica se a coluna alvo existe antes de indexar
    if "sentiment" in reviews.columns:
        indexer = StringIndexer(inputCol="sentiment", outputCol="label")
        # O handleInvalid="skip" evita crash se aparecer uma label nova inesperada
        reviews = indexer.fit(reviews).setHandleInvalid("skip").transform(reviews)

    else:
        grava_log("AVISO: Coluna 'sentiment' não encontrada. Pulando StringIndexer.", bucket_obj, log_file)

    # Limpeza com Regex (Encadeamento otimizado)
    # Remove tags HTML, caracteres especiais e espaços extras
    df_clean = reviews.withColumn("review", lower(regexp_replace(col("review"), r'<.*?>', ''))) \
                      .withColumn("review", regexp_replace(col("review"), r'[^a-z0-9 ]', '')) \
                      .withColumn("review", regexp_replace(col("review"), r'\s+', ' '))

    # Tokenização
    regex_tokenizer = RegexTokenizer(inputCol="review", outputCol="words", pattern="\\W")
    df_tokenized = regex_tokenizer.transform(df_clean)

    # StopWords
    remover = StopWordsRemover(inputCol="words", outputCol="filtered")
    feature_data = remover.transform(df_tokenized)

    """
      (PONTO CRÍTICO DE PERFORMANCE)
      Como feature_data será usado por HashingTF e Word2Vec, DEVEMOS colocar em cache.
      Se não fizer isso, o Spark vai rodar todos os regex acima duas vezes.
    """
    feature_data.cache()
   
    # Força a materialização do cache contando linhas (opcional, mas bom para debug)
    qtd_processada = feature_data.count()
    grava_log(f"Dados prontos para vetorização. Linhas: {qtd_processada}", bucket_obj, log_file)

    # 4. Feature Engineering (Pipeline Duplo: TF-IDF vs Word2Vec)
    
    # A) Pipeline TF-IDF
    hashingTF = HashingTF(inputCol="filtered", outputCol="raw_htf", numFeatures=4096)
    HTFdata = hashingTF.transform(feature_data)
    HTFdata.name = 'HTF' # Atribuir .name ao DF não é persistente no Spark, mas funciona para passagem local

    idf = IDF(inputCol="raw_htf", outputCol="features")
    idfModel = idf.fit(HTFdata)
    TFIDFdata = idfModel.transform(HTFdata)
    TFIDFdata.name = 'TFIDF'

    # B) Pipeline Word2Vec
    # vectorSize=100 é pesado. Se o cluster for pequeno (m5.xlarge), monitore a memória.
    word2Vec = Word2Vec(vectorSize=100, minCount=5, inputCol="filtered", outputCol="features_w2v")
    model_w2v = word2Vec.fit(feature_data)
    W2Vdata_raw = model_w2v.transform(feature_data)
    
    scaler = MinMaxScaler(inputCol="features_w2v", outputCol="features")
    W2Vdata = scaler.fit(W2Vdata_raw).transform(W2Vdata_raw)
    W2Vdata.name = 'W2V'

    # 5. Salvamento (Data Lakehouse Layer)
    grava_log("Salvando dados transformados no S3 (formato Parquet)...", bucket_obj, log_file)
    
    # Dica: Certifique-se que salvar_dataframe_s3 usa mode("overwrite") e format("parquet")
    salvar_dataframe_s3(HTFdata, f"{base_s3}/dados/processados/HTF")
    salvar_dataframe_s3(TFIDFdata, f"{base_s3}/dados/processados/TFIDF")
    salvar_dataframe_s3(W2Vdata, f"{base_s3}/dados/processados/W2V")

    # Limpeza de memória
    reviews.unpersist() # Libera o cache do CSV original
    # feature_data.unpersist() # Não liberar ainda se for retornar para uso imediato no ML
    
    return HTFdata, TFIDFdata, W2Vdata