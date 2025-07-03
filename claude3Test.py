import boto3
import json

# Initialize Bedrock Runtime client
client = boto3.client("bedrock-runtime", region_name="us-east-2")

# Prepare request payload in proper Anthropic format
payload = {
    "anthropic_version": "bedrock-2023-05-31",
    "messages": [
        {"role": "user", "content": "what is the most recent information you currently have access to?"}
    ],
    "max_tokens": 1000
}

# Invoke model with streaming response
response = client.invoke_model_with_response_stream(
    modelId="us.anthropic.claude-3-haiku-20240307-v1:0",  # Must be Inference Profile ARN or valid ID
    body=json.dumps(payload)
)

# Stream and print output
print("\n📝 Claude 3 Response:")

for event in response["body"]:
    if "chunk" in event:
        chunk_data = json.loads(event["chunk"]["bytes"].decode("utf-8"))
        delta = chunk_data.get("delta", {})
        content = delta.get("text", "")
        print(content, end="", flush=True)

print("\n✅ Done.")
