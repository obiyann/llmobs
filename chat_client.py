import requests
import json
import sys

def chat_with_ai(api_url):
    # Start the conversation
    conversation_state = 'START'
    
    # Initial request to start the conversation
    response = requests.post(
        api_url,
        json={'conversation_state': conversation_state}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("\n" + data.get('message', ''))
        conversation_state = data.get('conversation_state')
    else:
        print(f"Error: Failed to start conversation. Status code: {response.status_code}")
        return

    # Main chat loop
    while True:
        # Get user input
        prompt = input("\nYou: ").strip()
        
        if not prompt:
            continue
            
        # Send the request to the Lambda function
        response = requests.post(
            api_url,
            json={
                'conversation_state': conversation_state,
                'prompt': prompt
            }
        )
        
        if response.status_code != 200:
            print(f"Error: Request failed with status code {response.status_code}")
            print(response.text)
            continue
            
        # Parse and display the response
        data = response.json()
        
        # Check if the conversation is ending
        if data.get('conversation_state') == 'END':
            print("\nAssistant: " + data.get('message', ''))
            break
            
        # Display the AI's response
        print("\nAssistant: " + data.get('answer', ''))
        
        # Update conversation state
        conversation_state = data.get('conversation_state')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python chat_client.py <api_gateway_url>")
        print("Example: python chat_client.py https://your-api-gateway-url.amazonaws.com/stage/")
        sys.exit(1)
        
    api_url = sys.argv[1]
    print("\nWelcome to the AI Chat Client!")
    print("Type 'exit', 'quit', or 'bye' to end the conversation.")
    print("Press Ctrl+C to force quit.")
    
    try:
        chat_with_ai(api_url)
    except KeyboardInterrupt:
        print("\nChat session terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}") 