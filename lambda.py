from typing import Optional, Tuple
import json
import os
from phase2 import AmorisChatbot


def get_country_from_code(chat_id: str) -> str:
    """
    Determina el país basado en el código de país en el chat_id.
    """
    country_codes = {
        "54": "Argentina",
        "1": "Canada | USA",
        "44": "Reino Unido",
        "65": "Singapur",
        "61": "Australia",
        "234": "Nigeria",
        "593": "Ecuador",
        "34": "España",
        "52": "Mexico",
        "57": "Colombia",
        "58": "Venezuela",
    }

    # Buscar el código más largo que coincida con el inicio del chat_id
    for code in sorted(country_codes.keys(), key=len, reverse=True):
        if chat_id.startswith(code):
            return country_codes[code]

    # Si no encuentra coincidencia, retorna Belgica
    return "Belgica"


def validate_event(event: dict) -> Optional[Tuple[str, str, str, str]]:
    """
    Validate the incoming Lambda event from WhatsApp Green API.

    Args:
        event: The Lambda event dictionary

    Returns:
        Tuple[str, str, str, str]: A tuple containing (query, name, country, destinatario) if valid
        None: If the event is invalid
    """
    try:
        # Obtener y parsear el body del evento
        body = json.loads(event["Records"][0]["body"])

        # 1. Validar typeWebhook
        if body.get("typeWebhook") != "incomingMessageReceived":
            print("Invalid webhook type")
            return None

        # 2. Validar typeInstance
        if body.get("instanceData", {}).get("typeInstance") != "whatsapp":
            print("Invalid instance type")
            return None

        # 3. Validar idInstance
        expected_instance_id = int(
            os.getenv("WHATSAPP_INSTANCE_ID", "1101786874")
        )
        if (
            body.get("instanceData", {}).get("idInstance")
            != expected_instance_id
        ):
            print("Invalid instance ID")
            return None

        # 4. Validar typeMessage
        if body.get("messageData", {}).get("typeMessage") != "textMessage":
            print("Invalid message type")
            return None

        # 5. Obtener el mensaje de texto (query)
        query = (
            body.get("messageData", {})
            .get("textMessageData", {})
            .get("textMessage")
        )
        if not query:
            print("Missing text message")
            return None

        # 6. Obtener el nombre del remitente
        sender_name = body.get("senderData", {}).get("senderName")
        if not sender_name:
            print("Missing sender name")
            return None

        # 7. Obtener el chat ID (destinatario)
        chat_id = body.get("senderData", {}).get("chatId")
        if not chat_id:
            print("Missing chat ID")
            return None

        # 8. Determinar el país basado en el código del chat ID
        country = get_country_from_code(chat_id)

        return query, sender_name, country, chat_id

    except Exception as e:
        print(f"Error parsing event body: {str(e)}")
        return None


def create_response(status_code: int, body: dict) -> dict:
    """
    Create a properly formatted API Gateway response.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }


def handler(event: dict, context) -> dict:
    """
    Main Lambda handler function.
    """
    try:
        # Print the incoming event
        print(f"Received event from green-api: {json.dumps(event)}")

        # Validate the event
        validation_result = validate_event(event)
        if validation_result is None:
            return create_response(400, {"error": "Invalid request format"})

        # Desempaquetar los valores solo si la validación fue exitosa
        query, nombre_usuario, nacionalidad_usuario, destinatario = (
            validation_result
        )

        # Initialize the chatbot and process the query
        chatbot = AmorisChatbot()
        print(f"Processing query: {query}")
        response = chatbot.process_query(
            query, nombre_usuario, nacionalidad_usuario
        )
        print(f"Generated response que le tengo que mandar a {destinatario}: {response}")

        return create_response(200, {"message": response, "status": "success"})

    except ValueError as ve:
        # Error específico para el caso de desempaquetado de tupla fallido
        print(f"Error unpacking validation result: {str(ve)}")
        return create_response(400, {"error": "Invalid data format"})

    except Exception as e:
        # Cualquier otro error no esperado
        print(f"Error processing request: {str(e)}")
        return create_response(
            500, {"error": "Internal server error", "details": str(e)}
        )
