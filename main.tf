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

# Rol de IAM para Lambda
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
      }
    ]
  })
}

# Política para logs de CloudWatch
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Función Lambda
resource "aws_lambda_function" "amoris_chatbot" {
  filename         = "lambda_package.zip"
  function_name    = "amoris-chatbot"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda.handler"
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      REDIS_HOST     = var.redis_host
      REDIS_PORT     = var.redis_port
      REDIS_PASSWORD = var.redis_password
      OPENAI_API_KEY = var.openai_api_key
    }
  }
}

# Log group para CloudWatch
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/amoris-chatbot"
  retention_in_days = 14
}

# Variables
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

# Outputs
output "lambda_function_arn" {
  value = aws_lambda_function.amoris_chatbot.arn
}

output "lambda_function_name" {
  value = aws_lambda_function.amoris_chatbot.function_name
}

output "cloudwatch_log_group" {
  value = aws_cloudwatch_log_group.lambda_logs.name
}