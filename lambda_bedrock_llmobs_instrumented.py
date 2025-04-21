import json
import boto3
from ddtrace.llmobs.decorators import *

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
@workflow()
def get_model_response(prompt, matching_model):
    LLMObs.annotate(
        input_data=prompt,
    )
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
    output = response_body.get('content')[0].get('text')
    LLMObs.annotate(
        output_data=output,
    )
    return response_body.get('content')[0].get('text')

@task()
def categorize_prompt(prompt):
    # Create a system prompt for categorization
    system_prompt = """You are a prompt categorizer. Your task is to analyze the user's prompt and categorize it into one of the following categories:
    - GENERAL: General questions or conversations
    - TECHNICAL: Questions about technology, programming, or technical topics
    - CREATIVE: Requests for creative content, stories, or artistic ideas
    - ANALYTICAL: Questions requiring analysis, comparison, or evaluation
    - PERSONAL: Questions about personal experiences or opinions
    - OTHER: Any other type of prompt that doesn't fit the above categories
    
    Respond with ONLY the category name in capital letters.

    The prompt to categorize is: """

    LLMObs.annotate(
        input_data=system_prompt,
    )

    # The payload for categorization
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 50,
        "messages": [
            {
                "role": "user",
                "content": system_prompt + prompt
            }
        ],
        "temperature": 0.1,  # Lower temperature for more consistent categorization
        "top_p": 1,
    })

    # Get the categorization from the model
    response = bedrock_runtime.invoke_model(
        body=body,
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        accept='application/json',
        contentType='application/json'
    )

    response_body = json.loads(response.get('body').read())
    category = response_body.get('content')[0].get('text').strip()
    LLMObs.annotate(
        output_data=category,
    )
    return category

@agent()
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

    LLMObs.annotate(
        input_data=prompt,
    )
    
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

    # Categorize the prompt before getting the response
    category = categorize_prompt(prompt)

    # Get the response from the model
    answer = get_model_response(prompt, None)  # Model ID is hardcoded now

    LLMObs.annotate(
        output_data=answer,
    )

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
            'category': category,
            'conversation_state': 'CHATTING'
        })
    }
