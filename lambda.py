from typing import Dict, Any, Optional
import json
import logging
import sys
from phase2 import AmorisChatbot

# Configure logging to write to CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Add stdout handler to ensure print() statements are captured
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_handler)

def setup_logger() -> None:
    """Configure logging format for better CloudWatch readability."""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    stdout_handler.setFormatter(formatter)

def validate_event(event: Dict[str, Any]) -> Optional[str]:
    """
    Validate the incoming Lambda event.
    
    Args:
        event: The Lambda event dictionary
        
    Returns:
        Optional[str]: The user query if valid, None if invalid
    """
    try:
        body = (
            json.loads(event['body']) 
            if isinstance(event.get('body'), str) 
            else event.get('body')
        )
        
        if not body or 'query' not in body:
            logger.error("Invalid request body: missing 'query' field")
            return None
            
        return body['query']
        
    except Exception as e:
        logger.error(f"Error parsing event body: {str(e)}")
        return None

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a properly formatted API Gateway response.
    
    Args:
        status_code: HTTP status code
        body: Response body dictionary
        
    Returns:
        Dict containing the formatted response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler function.
    
    Args:
        event: Lambda event dictionary
        context: Lambda context object
        
    Returns:
        API Gateway response dictionary
    """
    # Setup logging for CloudWatch
    setup_logger()
    
    # Log the incoming event
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Validate the event
    query = validate_event(event)
    if not query:
        return create_response(400, {'error': 'Invalid request format'})
    
    try:
        # Initialize the chatbot
        chatbot = AmorisChatbot()
        
        # Process the query
        logger.info(f"Processing query: {query}")
        response = chatbot.process_query(query)
        logger.info(f"Generated response: {response}")
        
        return create_response(200, {
            'message': response,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'details': str(e)
        })