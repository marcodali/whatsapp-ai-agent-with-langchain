package main

import (
	"context"
	"encoding/json"
	"log"
	"os"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/sqs"
)

type Response events.APIGatewayProxyResponse

func handler(ctx context.Context, request events.APIGatewayProxyRequest) (Response, error) {
	// Configurar el cliente de AWS
	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		log.Printf("unable to load SDK config, %v", err)
		return Response{StatusCode: 500}, err
	}

	// Crear cliente SQS
	sqsClient := sqs.NewFromConfig(cfg)

	// Obtener URL de la cola desde variables de entorno
	queueURL := os.Getenv("QUEUE_URL")

	// Enviar mensaje a SQS
	_, err = sqsClient.SendMessage(ctx, &sqs.SendMessageInput{
		QueueUrl:    &queueURL,
		MessageBody: &request.Body,
	})

	if err != nil {
		log.Printf("error sending message to SQS: %v", err)
		return Response{StatusCode: 500}, err
	}

	// Preparar respuesta
	response := Response{
		StatusCode: 200,
		Headers: map[string]string{
			"Content-Type": "application/json",
		},
	}

	body, _ := json.Marshal(map[string]string{
		"message": "Request accepted for processing",
	})
	response.Body = string(body)

	return response, nil
}

func main() {
	lambda.Start(handler)
}