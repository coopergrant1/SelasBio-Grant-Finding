import boto3

# Initialize Bedrock client
client = boto3.client('bedrock-runtime', region_name='us-east-2')

# Claude 3 Haiku model ID may vary by region; check Bedrock docs or console
model_id = "anthropic.claude-3-haiku-20240307-v1:0"

# Your prompt
prompt_text = "Explain quantum computing simply."

# Bedrock expects Anthropic-style message formatting
payload = {
    "prompt": f"\n\nHuman: {prompt_text}\n\nAssistant:",
    "max_tokens_to_sample": 500,
    "temperature": 0.7
}

response = client.invoke_model(
    modelId=model_id,
    body=str(payload).replace("'", '"'),  # Bedrock expects double quotes in JSON
    accept='application/json',
    contentType='application/json'
)

# Parse output
output = response['body'].read().decode('utf-8')
print(output)
