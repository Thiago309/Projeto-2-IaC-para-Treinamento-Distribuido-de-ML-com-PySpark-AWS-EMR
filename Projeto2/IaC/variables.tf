# Definição de Variáveis

variable "region" {
  type        = string
  description = "Local de provisionamento dos serviços"
}

variable "project" {
  type        = string
  description = "Nome do projeto"
}     

variable "owner" {
  type        = string
  description = "Mantedor do projeto"
}

variable "environment" {
  type        = string
  description = "Tipo de ambiente"
}

# Variaveis para o bucket S3

variable "name_bucket" {
  type        = string
  description = "Nome do bucket"
}

variable "versioning_bucket" {
  type        = string
  description = "Define se o versionamento do bucket estará habilitado"
}

variable "files_bucket" {
  type        = string
  description = "Pasta de onde os scripts python serão obtidos para o processamento"
  default     = "./pipeline"
}

variable "files_data" {
  type        = string
  description = "Pasta de onde os dados serão obtidos"
  default     = "./dados"
}

variable "files_bash" {
  type        = string
  description = "Pasta de onde os scripts bash serão obtidos"
  default     = "./scripts"
}


# Variaveis para o Cluster EMR

variable "name_emr" {
  type        = string
  description = "Nome do cluster EMR"
}

variable "name_ssh" {
  type        = string
  description = "Nome da chave de conexão ssh"
}

variable "emr_release_label" {
  type        = string
  description = "Versão do serviço EMR"
}

variable "emr_man_instance_type" {
  type        = string
  description = "Tipo de instancia Master"
}

variable "emr_core_instance_type" {
  type        = string
  description = "Tipo de instancia worker"
}

variable "emr_core_instance_count" {
  type        = string
  description = "Numero de instancias workers em um nó"
}