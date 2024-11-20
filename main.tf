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

# S3 Bucket para lambdas y capas
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

# Subir archivo de Lambda Go
resource "aws_s3_object" "go_lambda" {
  bucket = aws_s3_bucket.lambda_bucket.bucket
  key    = "functions/receiver.zip"
  source = "receiver.zip"
  acl    = "private"
}

# Crear SQS Queue
resource "aws_sqs_queue" "chatbot_queue" {
  name                      = "amoris-chatbot-queue"
  message_retention_seconds = 1209600 # 14 días
  visibility_timeout_seconds = 60
}

# EventBridge Rule
resource "aws_cloudwatch_event_rule" "sqs_events" {
  name        = "capture-sqs-messages"
  description = "Capture messages added to SQS queue"

  event_pattern = jsonencode({
    source      = ["aws.sqs"]
    detail-type = ["AWS API Call via CloudTrail"]
    detail = {
      eventSource = ["sqs.amazonaws.com"]
      eventName   = ["SendMessage"]
      requestParameters = {
        queueUrl = [aws_sqs_queue.chatbot_queue.id]
      }
    }
  })
}

# EventBridge Target
resource "aws_cloudwatch_event_target" "sqs_to_lambda" {
  rule      = aws_cloudwatch_event_rule.sqs_events.name
  target_id = "ProcessSQSMessage"
  arn       = aws_lambda_function.amoris_chatbot.arn
}

# Capas Lambda
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

# Rol IAM para Lambda Go
resource "aws_iam_role" "go_lambda_role" {
  name = "amoris_chatbot_go_lambda_role"
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

# Política para que Lambda Go pueda escribir en SQS
resource "aws_iam_role_policy" "go_lambda_sqs" {
  name = "sqs_access"
  role = aws_iam_role.go_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:GetQueueUrl"
        ]
        Resource = [aws_sqs_queue.chatbot_queue.arn]
      }
    ]
  })
}

# Política de logs para Lambda Go
resource "aws_iam_role_policy_attachment" "go_lambda_logs" {
  role       = aws_iam_role.go_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Rol IAM para Lambda Python
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

# Política para que Lambda Python pueda leer de SQS
resource "aws_iam_role_policy" "python_lambda_sqs" {
  name = "sqs_access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = [aws_sqs_queue.chatbot_queue.arn]
      }
    ]
  })
}

# Política de logs para Lambda Python
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Grupos de logs en CloudWatch
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/amoris-chatbot"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "go_lambda_logs" {
  name              = "/aws/lambda/amoris-chatbot-receiver"
  retention_in_days = 14
}

# URL para la Lambda Go
resource "aws_lambda_function_url" "receiver_url" {
  function_name      = aws_lambda_function.receiver.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
  }
}

# Lambda Go para recibir requests
resource "aws_lambda_function" "receiver" {
  filename         = "receiver.zip"
  function_name    = "amoris-chatbot-receiver"
  role            = aws_iam_role.go_lambda_role.arn
  handler         = "receiver"
  runtime         = "provided.al2"
  architectures   = ["arm64"]
  timeout         = 10
  memory_size     = 128

  environment {
    variables = {
      QUEUE_URL = aws_sqs_queue.chatbot_queue.url
    }
  }
}

# Lambda Python principal
resource "aws_lambda_function" "amoris_chatbot" {
  filename         = "package.zip"
  function_name    = "amoris-chatbot"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda.handler"
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256
  layers          = [
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
      QUEUE_URL      = aws_sqs_queue.chatbot_queue.url
    }
  }
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
output "receiver_lambda_url" {
  description = "URL de la función Lambda Go"
  value       = aws_lambda_function_url.receiver_url.function_url
}

output "python_lambda_arn" {
  description = "ARN de la función Lambda Python"
  value       = aws_lambda_function.amoris_chatbot.arn
}

output "sqs_queue_url" {
  description = "URL de la cola SQS"
  value       = aws_sqs_queue.chatbot_queue.url
}

output "cloudwatch_log_groups" {
  value = {
    python = aws_cloudwatch_log_group.lambda_logs.name
    go     = aws_cloudwatch_log_group.go_lambda_logs.name
  }
}