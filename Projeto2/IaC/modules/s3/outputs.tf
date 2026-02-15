# Output utilizado para retornar o nome do bucket que será utilizado no script python projeto2.py 
output "final_bucket_name" {
  description = "Nome final do bucket criado"
  value       = aws_s3_bucket.create_bucket.bucket
}