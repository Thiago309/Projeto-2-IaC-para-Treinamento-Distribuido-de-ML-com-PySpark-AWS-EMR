# Projeto 2 - Deploy do Stack de Treinamento Distribuído de Machine Learning com PySpark no Amazon EMR
# Script de Definição de Valores de Variáveis

# Região para provisionar os serviços AWS
region      = "us-east-2"

# Nome do projeto
project     = "p2-pipeline-ML"

# Nome da chave SSH
name_ssh    = "deployer"

# Mantedor do projeto
owner       = "thiago-vinicius"

# Ambiente 
environment = "EMR"

# etiquetas de metadados
tags        = "projeto2"


# --- Grupo de Serviços ---


# 1.EMR

# Versão do EMR
emr_release_label       = "emr-7.12.0"

# Instancia Master
emr_man_instance_type   = "m5.4xlarge"

# Instancia dos workers
emr_core_instance_type  = "m5.2xlarge"

# Numero de workers
emr_core_instance_count = "2"

applications = ["Hadoop", "Spark"]



# 2.Bucket S3

# Nome do bucket para o pipeline
name_bucket       = "bucket-ML-pipeline"

# Nome do bucket para arquivos de log do EMR
name_emr          = "cluster-p2-EMR"

# Opção de habilitar versionamento do bucket s3
versioning_bucket = "Enabled"

files_bucket      = "./pipeline"
files_data        = "./dados"
files_bash        = "./scripts"