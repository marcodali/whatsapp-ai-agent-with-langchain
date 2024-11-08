import json
from phase2 import AmorisChatbot
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
chatbot = AmorisChatbot()

@logger.inject_lambda_context
def lambda_handler(event: dict, context: LambdaContext):
    """
    AWS Lambda handler for the Amoris chatbot.
    
    Expected event format for WhatsApp:
    {
        "body": {
            "message": {
                "text": "busco doctora colombiana"
            },
            "from": "whatsapp_user_id"
        }
    }
    """
    try:
        # Parse the incoming webhook from WhatsApp
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', {}).get('text', '')
        user_id = body.get('from', 'unknown_user')
        
        if not message:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No message provided'
                })
            }
        
        # Process the message through the chatbot
        response = chatbot.process_query(message)
        
        # Format response for WhatsApp API
        whatsapp_response = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': user_id,
            'type': 'text',
            'text': {
                'body': response
            }
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(whatsapp_response),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
    except Exception as e:
        logger.exception("Error processing message")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }