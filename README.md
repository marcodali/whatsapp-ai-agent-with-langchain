# Talk with Your Redis Database: A RAG Application Using Redis Vector Database and AWS Lambda

This repository provides a guide to setting up a Retrieval-Augmented Generation (RAG) application using Redis as the primary database for fast and scalable information retrieval. Instead of relying on traditional SQL databases, this project leverages Redis Vector Database to store and search embeddings, enabling rapid access to relevant data. The deployment is managed using AWS Lambda and Terraform, ensuring a production-ready environment.

## Tech Stack

- **Green API**: Utilizada en lugar de la API oficial de Meta para WhatsApp Business debido a su facilidad de uso y flexibilidad.
- **Redis Vector Database**: Empleada en lugar de bases de datos SQL tradicionales para un almacenamiento y búsqueda de embeddings más eficientes.
- **Python 3.11**: Incluye librerías como `langchain`, `openai`, y `redis` para facilitar la integración de la funcionalidad de chat y gestión de vectores.
- **AWS Lambda y Terraform**: Para un entorno de despliegue sin servidores, usando Terraform para la gestión de infraestructura.
- **text-embedding-3-small**: Seleccionado para embeddings por su balance entre rendimiento y tamaño.
- **gpt-4o-mini**: Utilizado para capacidades de chat, ofreciendo una alternativa más ligera a `gpt-4-turbo`.


## Layers Generation Prior to Deployment
To deploy the project on an `x86_64` AWS Lambda environment, you need to create the required layers using the `public.ecr.aws/lambda/python:3.11` Docker image.

Follow these steps:

1. Navigate to the `layers/` folder.
2. Build and run the Docker container using the provided Dockerfile. `docker build -t lambda-builder .`
3. Inside the running container, execute the commands listed in the `build_layers.sh` file.
4. Copy the generated `.zip` files from the container to the project's root directory.


## Deploy to AWS Lambda
To deploy the application to AWS Lambda using Terraform, follow these steps:

```bash
bash build_lambdas.sh
terraform init
terraform plan
terraform apply
```

## Test
Send a **POST** request to `Go Endpoint` with a json body:

```json
{
  "query": "quiero una chica que hable ingles y que sea un reto para mi a nivel intelectual pero al mismo tiempo me sea cariñosa y comprensiva"
}
```

The response (on Whatsapp) will be something like:
```python
"...es una psicóloga apasionada que... ...Su carrera implica un alto nivel de análisis y pensamiento crítico, lo que puede ofrecerte el reto intelectual que buscas..."
```