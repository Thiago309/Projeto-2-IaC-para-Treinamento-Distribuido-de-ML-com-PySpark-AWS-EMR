# Nome do arquivo: p2_processamento.py
from pyspark.sql.functions import col, lower, regexp_replace, count, when
from pyspark.ml.feature import StringIndexer, RegexTokenizer, StopWordsRemover, HashingTF, IDF, Word2Vec, MinMaxScaler

# IMPORT CORRIGIDO AQUI:
from p2_log import grava_log, salvar_dataframe_s3

def calcula_valores_nulos_otimizado(df):
    """
    Calcula nulos de todas as colunas em uma única ação do Spark.
    """
    expressoes = [count(when(col(c).isNull(), c)).alias(c) for c in df.columns]
    return df.select(expressoes).collect()[0].asDict()

def limpa_transforma_dados(spark, bucket_obj, nome_bucket, log_file):
    
    base_s3 = f"s3://{nome_bucket}"
    grava_log("Iniciando Módulo de Processamento...", bucket_obj, log_file)

    try:
        path_csv = f"{base_s3}/dados/dataset.csv"
        grava_log(f"Lendo arquivo: {path_csv}", bucket_obj, log_file)
        
        reviews = spark.read.csv(path_csv, header=True, escape="\"")
        reviews.cache()
        
    except Exception as e:
        grava_log(f"ERRO FATAL ao ler CSV: {str(e)}", bucket_obj, log_file)
        raise e

    # 2. Limpeza de Nulos
    nulos = calcula_valores_nulos_otimizado(reviews)
    if sum(nulos.values()) > 0:
        grava_log(f"Removendo linhas nulas: {nulos}", bucket_obj, log_file)
        reviews = reviews.dropna()
    
    # 3. Processamento de Texto (NLP)
    indexer = StringIndexer(inputCol="sentiment", outputCol="label")
    df = indexer.fit(reviews).transform(reviews)

    df = df.withColumn("review", regexp_replace(col("review"), '<.*/>', '')) \
           .withColumn("review", regexp_replace(col("review"), '[^A-Za-z ]+', '')) \
           .withColumn("review", regexp_replace(col("review"), ' +', ' ')) \
           .withColumn("review", lower(col("review")))

    regex_tokenizer = RegexTokenizer(inputCol="review", outputCol="words", pattern="\\W")
    df = regex_tokenizer.transform(df)

    remover = StopWordsRemover(inputCol="words", outputCol="filtered")
    feature_data = remover.transform(df)

    # 4. Feature Engineering
    hashingTF = HashingTF(inputCol="filtered", outputCol="raw_htf", numFeatures=4096)
    HTFdata = hashingTF.transform(feature_data)
    HTFdata.name = 'HTF'

    idf = IDF(inputCol="raw_htf", outputCol="features")
    idfModel = idf.fit(HTFdata)
    TFIDFdata = idfModel.transform(HTFdata)
    TFIDFdata.name = 'TFIDF'

    word2Vec = Word2Vec(vectorSize=100, minCount=5, inputCol="filtered", outputCol="features_w2v")
    model_w2v = word2Vec.fit(feature_data)
    W2Vdata_raw = model_w2v.transform(feature_data)
    
    scaler = MinMaxScaler(inputCol="features_w2v", outputCol="features")
    W2Vdata = scaler.fit(W2Vdata_raw).transform(W2Vdata_raw)
    W2Vdata.name = 'W2V'

    # 5. Salvamento
    grava_log("Salvando dados transformados...", bucket_obj, log_file)
    
    salvar_dataframe_s3(HTFdata, f"{base_s3}/dados/processados/HTF")
    salvar_dataframe_s3(TFIDFdata, f"{base_s3}/dados/processados/TFIDF")
    salvar_dataframe_s3(W2Vdata, f"{base_s3}/dados/processados/W2V")

    reviews.unpersist()
    return HTFdata, TFIDFdata, W2Vdata