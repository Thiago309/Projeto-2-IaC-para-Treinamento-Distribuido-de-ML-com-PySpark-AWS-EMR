# Nome do arquivo: p2_ml.py
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder

# IMPORT CORRIGIDO AQUI:
from p2_log import grava_log, salvar_modelo_s3

def treina_modelo(spark, df, bucket_obj, nome_bucket, dataset_name, log_file):
    
    grava_log(f"--- Iniciando Treino ML para: {dataset_name} ---", bucket_obj, log_file)
    
    train, test = df.randomSplit([0.7, 0.3], seed=42)
    
    lr = LogisticRegression(featuresCol='features', labelCol='label')
    
    paramGrid = (ParamGridBuilder()
                 .addGrid(lr.maxIter, [10, 20])
                 .addGrid(lr.regParam, [0.01, 0.1])
                 .build())
    
    crossval = CrossValidator(estimator=lr,
                              estimatorParamMaps=paramGrid,
                              evaluator=MulticlassClassificationEvaluator(metricName="accuracy"),
                              numFolds=2) 

    cv_model = crossval.fit(train)
    best_model = cv_model.bestModel
    
    predictions = cv_model.transform(test)
    evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
    accuracy = evaluator.evaluate(predictions) * 100
    
    grava_log(f"Modelo ({dataset_name}) - Acurácia Final: {accuracy:.2f}%", bucket_obj, log_file)
    
    caminho_modelo = f"s3://{nome_bucket}/output/modelos/LR_{dataset_name}"
    salvar_modelo_s3(best_model, caminho_modelo)

def cria_modelos_ml(spark, HTFdata, TFIDFdata, W2Vdata, bucket_obj, nome_bucket, log_file):
    
    datasets = [HTFdata, TFIDFdata, W2Vdata]
    
    for data in datasets:
        try:
            nome_ds = getattr(data, 'name', 'Unknown_Dataset') 
            treina_modelo(spark, data, bucket_obj, nome_bucket, nome_ds, log_file)
        except Exception as e:
            grava_log(f"ERRO ML ({nome_ds}): {str(e)}", bucket_obj, log_file)