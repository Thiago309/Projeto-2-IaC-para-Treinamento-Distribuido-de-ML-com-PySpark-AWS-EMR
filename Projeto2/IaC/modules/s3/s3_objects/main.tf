# Upload dos meus arquivos na maquina cliente para o bucket S3

variable "name_bucket" {}

variable "files_bucket" {}

variable "files_data" {}

variable "files_bash" {}

# python_scripts
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
  bucket = var.name_bucket
  key    = "dados-transformados/"
}

# cria uma pasta chamada logs
resource "aws_s3_object" "logs" {
  bucket = var.name_bucket
  key    = "logs/"
}

# crria uma pasta chamada output
resource "aws_s3_object" "output" {
  bucket = var.name_bucket
  key    = "output-jobs/"
}