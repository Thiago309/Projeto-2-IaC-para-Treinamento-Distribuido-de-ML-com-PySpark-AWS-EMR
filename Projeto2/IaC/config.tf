# Projeto 2 - Deploy do Stack de Treinamento Distribuído de Machine Learning com PySpark no Amazon EMR
# Configuração Para o Estado Remoto, Versão do Terraform e Provider

data "aws_caller_identity" "current" {}

# Versão do Terraform
terraform {
  required_version = "~> 1.7"

  # Provider AWS
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend usado para o estado remoto
  backend "s3" {
    encrypt = true
    # Este bucket deve ser criado manualmente no ambiente AWS
    bucket  = "p2-remote-state-${data.aws_caller_identity.current.account_id}"
    key     = "p2-ml.tfstate"
    region  = var.region
  }
}

# Região do provider
provider "aws" {
  region = "us-east-2"
}