# Talk with your redis database

This repo shows you how to use a redis database as the source of a fully operational production ready RAG app

## Stack

* Green api (russian) instead of official Meta Whatsapp business api
* Redis instead of the traditional boring SQL world (Postgres, Maria)
* Python instead of NodeJS
* AWS instead of Jupiter Notebook

## Parameter Store
```bash
aws ssm put-parameter --name "/amoris/openai_api_key" --value "tu-api-key" --type SecureString
aws ssm put-parameter --name "/amoris/redis_host" --value "tu-host" --type SecureString
aws ssm put-parameter --name "/amoris/redis_port" --value "tu-puerto" --type SecureString
aws ssm put-parameter --name "/amoris/redis_password" --value "tu-password" --type SecureString
```

## Deploy using SAM
```bash
sam build
sam deploy --guided
```