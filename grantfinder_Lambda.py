# grantsgov_lambda_claude.py

import requests
import boto3
import json

# =============================
# STEP 1: Query Grants.gov API
# =============================

def fetch_grantsgov_projects(query_text, limit=1000):
    url = "https://api.grants.gov/v1/api/search2"
    payload = {
        "keyword": query_text,
        "rows": limit,
        "oppStatuses": "forecasted|posted"
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Grants.gov API error: {response.status_code} - {response.text}")
    return response.json().get("data", {}).get("oppHits", [])

# =============================
# STEP 2: Claude 3 Bedrock Logic
# =============================

def query_claude(prompt_text, region="us-east-2"):
    client = boto3.client("bedrock-runtime", region_name=region)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {"role": "user", "content": prompt_text}
        ],
        "max_tokens": 500
    }
    response = client.invoke_model(
        modelId="us.anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps(body)
    )
    output = json.loads(response["body"].read().decode("utf-8"))
    return output.get("content", "No response from Claude.")

# =============================
# Lambda Entry Point
# =============================

def lambda_handler(event, context):
    query_text = event.get("query", "cancer")
    print(f"Fetching opportunities for: {query_text}")

    projects = fetch_grantsgov_projects(query_text)
    if not projects:
        return {
            "statusCode": 200,
            "body": json.dumps({"results": [], "message": "No opportunities found."})
        }

    print(f"Retrieved {len(projects)} opportunities.")

    formatted_projects = "\n".join(f"{i+1}. {p.get('title', '')}" for i, p in enumerate(projects[:20]))
    prompt = (
        f"You are an expert grants advisor. Here are some funding opportunities:\n\n{formatted_projects}\n\n"
        "Based on the user's query, recommend the most relevant ones with brief reasoning."
    )

    claude_response = query_claude(prompt)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Top opportunities selected by Claude:",
            "claude_response": claude_response
        })
    }
