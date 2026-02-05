# Projeto 2 - Deploy do Stack de Treinamento Distribuído de Machine Learning com PySpark no Amazon EMR
# Provisionamento dos recursos EMR


# Variaveis EMR
variable "name_emr" { }

variable "name_bucket" { }

variable "project" { }

variable "environment" { }

variable "tags" { }

variable "emr_release_label" { }

variable "applications" { }

variable "emr_release_label" { }

variable "emr_man_instance_type" { }

variable "emr_core_instance_type" { }

variable "emr_core_instance_count" { }


data "aws_caller_identity" "current" { }

# Recurso de criação do cluster EMR
resource "aws_emr_cluster" "emr_cluster" {
  name          = "${var.project}-emr-cluster-${var.environment}"
  release_label = var.emr_release_label
  applications  = var.applications
  tags = var.tags

  # Proteção contra término do cluster
  termination_protection = false
  
  # Mantém o job de processamento ativo
  keep_job_flow_alive_when_no_steps = false
  
  # URI da pasta com logs
  log_uri = "s3://${var.name_bucket}-${data.aws_caller_identity.current.account_id}/logs/"

  # Role IAM do serviço
  service_role = aws_iam_role.emr_service_role.arn

  # Atributos das Instâncias EC2 do cluster
  ec2_attributes {
    instance_profile = aws_iam_instance_profile.emr_ec2_instance_profile.arn
    emr_managed_master_security_group = aws_security_group.main_security_group.id
    emr_managed_slave_security_group = aws_security_group.core_security_group.id
  }

  # Tipo de instância do Master (NÃO É GRATUITO)
  master_instance_group {
    instance_type = var.emr_man_instance_type
  }

  # Tipo de instância dos workers (NÃO É GRATUITO)
  core_instance_group {
    instance_type  = var.emr_core_instance_type
    instance_count = var.emr_core_instance_count
  }

  # Executa o script de instalação do interpretador Python e pacotes adicionais
  bootstrap_action {
    name = "Instala pacotes python adicionais"
    path = "s3://${var.name_bucket}-${data.aws_caller_identity.current.account_id}/scripts/bootstrap.sh"
  }

  # Passos executados no cluster

  # 1- Copia os arquivos do S3 para as instâncias EC2 do cluster. Se falhar encerra o cluster.
  # 2- Copia os arquivos de log do S3 para as instâncias EC2 do cluster. Se falhar encerra o cluster.
  # 3- Executa script Python com o processamento do job. Se falhar, mantém o cluster ativo para investigar o que causou a falha.

  step = [
    {
      name              = "Copia scripts python para maquinas EC2"
      action_on_failure = "TERMINATE_CLUSTER"

      hadoop_jar_step = [
        {
          jar        = "command-runner.jar"
          args       = ["aws", "s3", "cp", "s3://${var.name_bucket}-${data.aws_caller_identity.current.account_id}/pipeline", "/home/hadoop/pipeline/", "--recursive"]
          main_class = ""
          properties = {}
        }
      ]
    },
    {
      name              = "Copia arquivos de log para maquinas EC2"
      action_on_failure = "TERMINATE_CLUSTER"

      hadoop_jar_step = [
        {
          jar        = "command-runner.jar"
          args       = ["aws", "s3", "cp", "s3://${var.name_bucket}-${data.aws_caller_identity.current.account_id}/logs", "/home/hadoop/logs/", "--recursive"]
          main_class = ""
          properties = {}
        }
      ]
    },
    {
      name              = "Executa script python"
      action_on_failure = "CONTINUE"

      hadoop_jar_step = [
        {
          jar        = "command-runner.jar"
          args       = ["spark-submit", "/home/hadoop/pipeline/projeto2.py"]
          main_class = ""
          properties = {}
        }
      ]
    }
  ]

  # Arquivo de configurações do Spark
  configurations_json = <<EOF
    [
    {
    "Classification": "spark-defaults",
      "Properties": {
      "spark.pyspark.python": "/home/hadoop/conda/bin/python",
      "spark.dynamicAllocation.enabled": "true",
      "spark.network.timeout":"800s",
      "spark.executor.heartbeatInterval":"60s"
      }
    }
  ]
  EOF
}