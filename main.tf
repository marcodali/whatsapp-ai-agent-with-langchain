terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ca-central-1"
}

# Crear bucket S3 para almacenar los paquetes de Lambda y capas
resource "aws_s3_bucket" "lambda_bucket" {
  bucket = "amoris-laboris-chatbot"
}

# Subir archivos de capas a S3
resource "aws_s3_object" "layer1" {
  bucket = aws_s3_bucket.lambda_bucket.bucket
  key    = "layers/langchain.zip"
  source = "langchain.zip"
  acl    = "private"
}

resource "aws_s3_object" "layer2" {
  bucket = aws_s3_bucket.lambda_bucket.bucket
  key    = "layers/openai.zip"
  source = "openai.zip"
  acl    = "private"
}

resource "aws_s3_object" "layer3" {
  bucket = aws_s3_bucket.lambda_bucket.bucket
  key    = "layers/redis.zip"
  source = "redis.zip"
  acl    = "private"
}

# Crear las capas de Lambda a partir de los archivos en S3
resource "aws_lambda_layer_version" "layer_langchain" {
  layer_name          = "amoris_chatbot_langchain"
  compatible_runtimes = ["python3.11"]
  s3_bucket           = aws_s3_bucket.lambda_bucket.bucket
  s3_key              = aws_s3_object.layer1.key
}

resource "aws_lambda_layer_version" "layer_openai" {
  layer_name          = "amoris_chatbot_openai"
  compatible_runtimes = ["python3.11"]
  s3_bucket           = aws_s3_bucket.lambda_bucket.bucket
  s3_key              = aws_s3_object.layer2.key
}

resource "aws_lambda_layer_version" "layer_redis" {
  layer_name          = "amoris_chatbot_redis"
  compatible_runtimes = ["python3.11"]
  s3_bucket           = aws_s3_bucket.lambda_bucket.bucket
  s3_key              = aws_s3_object.layer3.key
}

# Crear rol de IAM para la función Lambda
resource "aws_iam_role" "lambda_role" {
  name = "amoris_chatbot_lambda_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

# Asignar política para logs de CloudWatch al rol de IAM
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Grupo de logs en CloudWatch
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/amoris-chatbot"
  retention_in_days = 14
}

# Crear una URL directa para la función Lambda
resource "aws_lambda_function_url" "amoris_chatbot_url" {
  function_name      = aws_lambda_function.amoris_chatbot.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
  }
}

# Función Lambda principal
resource "aws_lambda_function" "amoris_chatbot" {
  filename         = "package.zip"
  function_name    = "amoris-chatbot"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda.handler"
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 256
  layers           = [
    aws_lambda_layer_version.layer_langchain.arn,
    aws_lambda_layer_version.layer_openai.arn,
    aws_lambda_layer_version.layer_redis.arn,
  ]

  environment {
    variables = {
      REDIS_HOST     = var.redis_host
      REDIS_PORT     = var.redis_port
      REDIS_PASSWORD = var.redis_password
      OPENAI_API_KEY = var.openai_api_key
    }
  }
}

# Variables sensibles
variable "redis_host" {
  description = "Redis host address"
  type        = string
  sensitive   = true
}

variable "redis_port" {
  description = "Redis port"
  type        = string
  sensitive   = true
}

variable "redis_password" {
  description = "Redis password"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

# Salidas
output "lambda_function_arn" {
  description = "ARN de la función Lambda"
  value       = aws_lambda_function.amoris_chatbot.arn
}

output "lambda_function_url" {
  description = "URL de la función Lambda"
  value       = aws_lambda_function_url.amoris_chatbot_url.function_url
}

output "layer_arns" {
  description = "ARNs de las capas de Lambda"
  value       = [
    aws_lambda_layer_version.layer_langchain.arn,
    aws_lambda_layer_version.layer_openai.arn,
    aws_lambda_layer_version.layer_redis.arn,
  ]
}

output "cloudwatch_log_group" {
  value = aws_cloudwatch_log_group.lambda_logs.name
}
