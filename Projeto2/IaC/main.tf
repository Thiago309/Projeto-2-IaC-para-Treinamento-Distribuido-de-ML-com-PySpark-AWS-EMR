# Projeto 2 - Deploy do Stack de Treinamento Distribuído de Machine Learning com PySpark no Amazon EMR
# Script Principal

provider "aws" {
  region  = var.region
}

# Locals
locals {
  tags = {
    "owner"   = var.owner
    "project" = var.project
    "stage"   = var.environment
  }
}

# Módulo de Armazenamento
module "s3" {
  source            = "./modules/s3"
  project           = var.project
  versioning_bucket = var.versioning_bucket
  name_bucket       = var.name_bucket
  files_bucket      = var.files_bucket
  files_data        = var.files_data
  files_bash        = var.files_bash
}

# Módulo de Processamento
module "emr" {
  source                  = "./modules/emr"
  name_emr                = var.name_emr
  name_bucket             = module.s3.final_bucket_name
  project                 = var.project 
  environment             = var.environment
  tags                    = local.tags
  emr_release_label       = var.emr_release_label
  applications            = ["Hadoop", "Spark"]
  emr_man_instance_type   = var.emr_man_instance_type
  emr_core_instance_type  = var.emr_core_instance_type
  emr_core_instance_count = var.emr_core_instance_count
  depends_on              = [module.s3]
}