import json
import boto3

# Bedrock client used to interact with APIs around models
bedrock = boto3.client(
    service_name='bedrock',
    region_name='us-east-1'
)

# Bedrock Runtime client used to invoke and question the models
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

def get_model_response(prompt, matching_model):
    # The payload to be provided to Bedrock 
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 200,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "top_p": 1,
    })

    # The actual call to retrieve an answer from the model
    response = bedrock_runtime.invoke_model(
        body=body,
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        accept='application/json',
        contentType='application/json'
    )

    response_body = json.loads(response.get('body').read())
    return response_body.get('content')[0].get('text')

def lambda_handler(event, context):
    # Get the conversation state from the event
    body = json.loads(event.get('body', '{}'))
    conversation_state = body.get('conversation_state', 'START')
    
    if conversation_state == 'START':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': "Welcome to the AI Chat! Please enter your question.",
                'conversation_state': 'CHATTING'
            })
        }
    
    # Get the user's prompt from the event body
    prompt = body.get('prompt', '')
    
    if prompt.lower() in ['exit', 'quit', 'bye']:
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': "Thank you for chatting! Goodbye!",
                'conversation_state': 'END'
            })
        }
    
    if not prompt:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': "Please provide a prompt in the request body",
                'conversation_state': 'CHATTING'
            })
        }

    # Get the response from the model
    answer = get_model_response(prompt, None)  # Model ID is hardcoded now

    return {
        'statusCode': 200,
        'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Content-Type': 'application/json'
            },
        'body': json.dumps({
            'answer': answer,
            'conversation_state': 'CHATTING'
        })
    }
