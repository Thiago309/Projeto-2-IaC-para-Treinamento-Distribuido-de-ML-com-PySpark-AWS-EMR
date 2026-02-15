from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder

# Import do módulo de log
from p2_log import grava_log, salvar_modelo_s3

def treina_modelo(spark, df, bucket_obj, nome_bucket, dataset_name, log_file):
    
    grava_log(f"--- Iniciando Treino ML para: {dataset_name} ---", bucket_obj, log_file)
    
    # Divide os dados
    train, test = df.randomSplit([0.7, 0.3], seed=42)
    
    # === OTIMIZAÇÃO CRÍTICA PARA EMR ===
    # Algoritmos iterativos (LR) + CrossValidator leem os dados muitas vezes.
    # Sem o cache, o Spark refaz toda a transformação (TF-IDF/W2V) a cada iteração.
    train.cache()
    
    # Força a materialização do cache e conta registros para log
    qtd_treino = train.count()
    grava_log(f"Dataset de Treino ({dataset_name}) em cache. Registros: {qtd_treino}", bucket_obj, log_file)

    lr = LogisticRegression(featuresCol='features', labelCol='label')
    
    # Grid de Hiperparâmetros
    paramGrid = (ParamGridBuilder()
                 .addGrid(lr.maxIter, [10, 20])
                 .addGrid(lr.regParam, [0.01, 0.1])
                 .build())
    
    crossval = CrossValidator(estimator=lr,
                              estimatorParamMaps=paramGrid,
                              evaluator=MulticlassClassificationEvaluator(metricName="accuracy"),
                              numFolds=2) # Mantive 2 para ser rápido no teste, produção use 3-5

    # O Treinamento pesado acontece aqui
    print(f"Treinando CrossValidator para {dataset_name}...")
    cv_model = crossval.fit(train)
    
    # Libera memória do cluster assim que o treino acabar
    train.unpersist()
    
    best_model = cv_model.bestModel
    # Opcional: Logar os melhores parâmetros
    print(f"Melhor RegParam para {dataset_name}: {best_model.getRegParam()}")

    # Avaliação
    predictions = cv_model.transform(test)
    evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
    accuracy = evaluator.evaluate(predictions) * 100
    
    grava_log(f"Modelo ({dataset_name}) - Acurácia Final: {accuracy:.2f}%", bucket_obj, log_file)
    
    # Salvamento do Modelo
    # Garante que não duplique 's3://' caso nome_bucket venha sujo
    bucket_clean = nome_bucket.replace("s3://", "")
    caminho_modelo = f"s3://{bucket_clean}/output/modelos/LR_{dataset_name}"
    
    salvar_modelo_s3(best_model, caminho_modelo)

def cria_modelos_ml(spark, HTFdata, TFIDFdata, W2Vdata, bucket_obj, nome_bucket, log_file):
    
    datasets = [HTFdata, TFIDFdata, W2Vdata]
    
    for data in datasets:
        # Recupera o nome atribuído no processamento anterior
        nome_ds = getattr(data, 'name', 'Unknown_Dataset') 
        
        try:
            treina_modelo(spark, data, bucket_obj, nome_bucket, nome_ds, log_file)
        except Exception as e:
            import traceback
            erro_msg = f"ERRO ML ({nome_ds}): {str(e)}\n{traceback.format_exc()}"
            grava_log(erro_msg, bucket_obj, log_file)