from typing import Optional, Tuple
import json
from phase2 import AmorisChatbot


def validate_event(event: dict) -> Optional[Tuple[str, str, str]]:
    """
    Validate the incoming Lambda event.
    
    Args:
        event: The Lambda event dictionary
        
    Returns:
        Tuple[str, str, str]: A tuple containing (query, name, country) if valid
        None: If the event is invalid
    """
    try:
        body = json.loads(event["Records"][0]["body"])
        if "query" not in body:
            print("Invalid message body: missing 'query' field")
            return None
        if "name" not in body:
            print("Invalid message body: missing 'name' field")
            return None
        if "country" not in body:
            print("Invalid message body: missing 'country' field")
            return None

        return body["query"], body["name"], body["country"]

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

    # Validate the event
    query, nombre_usuario, nacionalidad_usuario = validate_event(event)
    if not query:
        return create_response(400, {"error": "Invalid request format"})

    try:
        # Initialize the chatbot
        chatbot = AmorisChatbot()

        # Process the query
        print(f"Processing query: {query}")
        response = chatbot.process_query(query, nombre_usuario, nacionalidad_usuario)
        print(f"Generated response: {response}")

        return create_response(200, {"message": response, "status": "success"})

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return create_response(
            500, {"error": "Internal server error", "details": str(e)}
        )
