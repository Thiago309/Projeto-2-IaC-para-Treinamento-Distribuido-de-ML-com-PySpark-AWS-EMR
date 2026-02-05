# Projeto 2 - Deploy do Stack de Treinamento Distribuído de Machine Learning com PySpark no Amazon EMR
# Script de Definição de Valores de Variáveis

# Região para provisionar os serviços AWS
region = "us-east-2"

# Nome do projeto
project = "p2-pipeline-ML"

# Nome da chave SSH
name_ssh = "deployer"

# Mantedor do projeto
owner = "thiago-vinicius"

# Ambiente 
environment = "EMR"

# Grupo de Serviços

# 1.EMR

# Versão do EMR
emr_release_label = "emr-7.12.0"

# Instancia Master
emr_man_instance_type = "m5.xlarge"

# Instancia dos workers
emr_core_instance_type = "m5.xlarge"

# Numero de workers
emr_core_instance_count = "2"


# 2.Bucket S3


name_bucket       = "ML-Bucket"
name_emr          = "projeto2-logs"
versioning_bucket = "Enabled"
files_bucket      = "${path.module}/pipeline"
files_data        = "${path.module}/dados"
files_bash        = "${path.module}/scripts"