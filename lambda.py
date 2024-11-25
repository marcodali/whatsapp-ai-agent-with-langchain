from typing import Optional, Tuple
import json
import os
from phase2 import AmorisChatbot


def send_message_to_whatsapp(destinatario: str, mensaje: str):
    import requests

    url = f"https://api.green-api.com/waInstance{os.getenv('WHATSAPP_INSTANCE_ID')}/sendMessage/{os.getenv('API_TOKEN_INSTANCE')}"

    payload = {"chatId": destinatario, "message": mensaje}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    print(response.text.encode("utf8"))


def get_country_from_code(sender_phone_number: str) -> str:
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

    # Buscar el código más largo que coincida con el inicio del sender_phone_number
    for code in sorted(country_codes.keys(), key=len, reverse=True):
        if sender_phone_number.startswith(code):
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

        if not query.lower().startswith("deseo"):
            print("Si no lo DESEAS con fuerza no se va a cumplir")
            return None

        # 6. Como se llama el usuario que envió el mensaje
        sender_name = body.get("senderData", {}).get("senderName")
        if not sender_name:
            print("Missing sender name")
            return None

        # 7. A quien le respondo el mensaje
        sender_phone_number = body.get("senderData", {}).get("sender")
        if not sender_phone_number:
            print("Missing sender phone number")
            return None

        # 8. Determinar el país basado en el sender_phone_number
        country = get_country_from_code(sender_phone_number)

        return query, sender_name, country, sender_phone_number

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
        print(
            f"Received event from green-api: {json.loads(event['Records'][0]['body'])}"
        )

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
        response = chatbot.process_query(
            query, nombre_usuario, nacionalidad_usuario
        )
        print(
            f"A mi amigo {nombre_usuario} con número de telefono {destinatario} le voy a responder: {response}"
        )

        send_message_to_whatsapp(destinatario, response)

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
