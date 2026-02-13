# Módulo de armazenamento com bucket S3

variable "project" {}

variable "versioning_bucket" {}

variable "name_bucket" {}

variable "files_bucket" {}

variable "files_data" {}

variable "files_bash" {}

# Obtém informações da conta atual automaticamente
data "aws_caller_identity" "current" {}

# Criação do bucket
resource "aws_s3_bucket" "create_bucket" {

  bucket = "${var.name_bucket}-${data.aws_caller_identity.current.account_id}"

  force_destroy = true

  tags = {
    Name        = "Armazenamento dos Dados"
    Environment = var.project
  }
}

# Versionamento do bucket
resource "aws_s3_bucket_versioning" "versioning_bucket" {
  
  bucket = aws_s3_bucket.create_bucket.id
  versioning_configuration {status = var.versioning_bucket}
  depends_on = [aws_s3_bucket.create_bucket]
}

# Bloqueia acesso público
resource "aws_s3_bucket_public_access_block" "example" {

  bucket = aws_s3_bucket.create_bucket.id
  block_public_policy     = false
  restrict_public_buckets = false
}

# Upload dos arquivos S3

resource "aws_s3_object" "python_scripts" {
  for_each  = fileset("${var.files_bucket}/", "**/*")
  bucket    = aws_s3_bucket.create_bucket.id
  key       = "pipeline/${each.value}"
  source    = "${var.files_bucket}/${each.value}"
  etag      = filemd5("${var.files_bucket}/${each.value}")
}

# raw_data
resource "aws_s3_object" "raw_data" {
  for_each  = fileset("${var.files_data}/", "**/*")
  bucket    = aws_s3_bucket.create_bucket.id
  key       = "dados/${each.value}"
  source    = "${var.files_data}/${each.value}"
  etag      = filemd5("${var.files_data}/${each.value}")
}

# bash_scripts
resource "aws_s3_object" "bash_scripts" {
  for_each  = fileset("${var.files_bash}/", "**/*")
  bucket    = aws_s3_bucket.create_bucket.id
  key       = "scripts/${each.value}"
  source    = "${var.files_bash}/${each.value}"
  etag      = filemd5("${var.files_bash}/${each.value}")
}

# cria uma pasta chamada dados-transformados dentro do bucket s3
resource "aws_s3_object" "transformed_data" {
  bucket = aws_s3_bucket.create_bucket.id
  key    = "dados_transformados/"
}

# cria uma pasta chamada logs
resource "aws_s3_object" "logs" {
  bucket = aws_s3_bucket.create_bucket.id
  key    = "logs/"
}

# crria uma pasta chamada output
resource "aws_s3_object" "output" {
  bucket = aws_s3_bucket.create_bucket.id
  key    = "output_jobs/"
}