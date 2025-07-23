import urllib.request
import urllib.parse
import boto3
import json
import uuid
import time

# adding actual grant information + links? to claude output not just raw ai text

# v 3 has saved searches logic and fetch summary logic

# =============================
# STEP 1: Query Grants.gov API
# =============================

def fetch_grantsgov_projects(query_text, limit=30):
    url = "https://api.grants.gov/v1/api/search2"
    payload = {
        "keyword": query_text,
        "rows": limit,
        "oppStatuses": "forecasted|posted"
    }
    
    print(f"Requesting {limit} grants from Grants.gov API")
    
    # Convert payload to JSON and encode
    data = json.dumps(payload).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (compatible; GrantFinder/1.0)'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() != 200:
                raise Exception(f"Grants.gov API error: {response.getcode()}")
            
            response_data = json.loads(response.read().decode('utf-8'))
            grants = response_data.get("data", {}).get("oppHits", [])
            print(f"API returned {len(grants)} grants")
            
            # Ensure we don't exceed our limit
            return grants[:limit]
    except urllib.error.HTTPError as e:
        raise Exception(f"Grants.gov API error: {e.code} - {e.reason}")
    except Exception as e:
        raise Exception(f"Error fetching grants: {str(e)}")

# =============================
# STEP 2: Claude 3 Bedrock Logic
# =============================

def query_claude(prompt_text, region="us-east-2", max_tokens=1500):
    try:
        client = boto3.client("bedrock-runtime", region_name=region)
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {"role": "user", "content": prompt_text}
            ],
            "max_tokens": max_tokens
        }
        response = client.invoke_model(
            modelId="us.anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps(body)
        )
        output = json.loads(response["body"].read().decode("utf-8"))
        
        # Extract the actual text from Claude's response
        content = output.get("content", [])
        if content and isinstance(content, list) and len(content) > 0:
            return content[0].get("text", "No response from Claude.")
        else:
            return "No response from Claude."
            
    except Exception as e:
        print(f"Error querying Claude: {str(e)}")
        return f"Error: {str(e)}"
    
# =============================
# STEP 3: Saved Search Logic
# =============================

def save_search_to_memory(query, grants_data, problem=None, solution=None, claude_response=None):
    """Save search data to in-memory storage (replace with DynamoDB in production)"""
    search_id = str(uuid.uuid4())
    timestamp = int(time.time() * 1000)  # milliseconds
    
    search_data = {
        "id": search_id,
        "query": query,
        "timestamp": timestamp,
        "grants_found": len(grants_data) if grants_data else 0,
        "grants_data": grants_data,
        "problem_statement": problem,
        "solution_description": solution,
        "claude_response": claude_response,
        "analysis_completed": bool(claude_response)
    }
    
    # In production, save to DynamoDB instead
    # For now, we'll use a global variable (not recommended for production)
    if not hasattr(save_search_to_memory, "searches"):
        save_search_to_memory.searches = []
    
    save_search_to_memory.searches.append(search_data)
    return search_id

def get_saved_searches():
    """Get all saved searches"""
    if not hasattr(save_search_to_memory, "searches"):
        return []
    
    # Return searches sorted by timestamp (newest first)
    searches = save_search_to_memory.searches.copy()
    searches.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Return simplified data for list view
    return [
        {
            "id": search["id"],
            "query": search["query"],
            "timestamp": search["timestamp"],
            "grants_found": search["grants_found"],
            "problem_statement": search.get("problem_statement", ""),
            "analysis_completed": search["analysis_completed"]
        }
        for search in searches
    ]

def get_search_details(search_id):
    """Get detailed data for a specific search"""
    if not hasattr(save_search_to_memory, "searches"):
        return None
    
    for search in save_search_to_memory.searches:
        if search["id"] == search_id:
            return search
    return None

def delete_search(search_id):
    """Delete a saved search"""
    if not hasattr(save_search_to_memory, "searches"):
        return False
    
    save_search_to_memory.searches = [
        search for search in save_search_to_memory.searches 
        if search["id"] != search_id
    ]
    return True


# =============================
# Lambda Entry Point
# =============================

def lambda_handler(event, context):
    try:
        # Handle both direct invocation and API Gateway
        if 'body' in event:
            # API Gateway format
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Direct invocation
            body = event
        
        # Determine which step we're on
        step = body.get("step", "1")
        
        if step == "1":
            # STEP 1: Fetch grants based on keyword
            return handle_step_1(body)
        elif step == "2":
            # STEP 2: Match grants to problem/solution
            return handle_step_2(body)
        elif step == "get_saved_searches":
            # NEW: Get saved searches
            return handle_get_saved_searches()
        elif step == "get_search_details":
            # NEW: Get search details
            return handle_get_search_details(body)
        elif step == "delete_search":
            # NEW: Delete search
            return handle_delete_search(body)
        else:
            return create_error_response("Invalid step parameter")
    
    except Exception as e:
        print(f"Lambda error: {str(e)}")
        return create_error_response(str(e))
    
def handle_get_saved_searches():
    """Handle getting saved searches"""
    try:
        saved_searches = get_saved_searches()
        return create_success_response({
            "saved_searches": saved_searches,
            "total": len(saved_searches)
        })
    except Exception as e:
        return create_error_response(f"Error getting saved searches: {str(e)}")

def handle_get_search_details(body):
    """Handle getting search details"""
    try:
        search_id = body.get("search_id")
        if not search_id:
            return create_error_response("Search ID is required")
        
        search_details = get_search_details(search_id)
        if not search_details:
            return create_error_response("Search not found")
        
        return create_success_response({
            "search_details": search_details
        })
    except Exception as e:
        return create_error_response(f"Error getting search details: {str(e)}")

def handle_delete_search(body):
    """Handle deleting a search"""
    try:
        search_id = body.get("search_id")
        if not search_id:
            return create_error_response("Search ID is required")
        
        success = delete_search(search_id)
        if not success:
            return create_error_response("Search not found or could not be deleted")
        
        return create_success_response({
            "message": "Search deleted successfully"
        })
    except Exception as e:
        return create_error_response(f"Error deleting search: {str(e)}")

def handle_step_1(body):
    """Step 1: Fetch grants based on keyword search"""
    try:
        query_text = body.get("query", "")
        if not query_text:
            return create_error_response("Query text is required for step 1")
        
        print(f"Step 1: Fetching opportunities for keyword: {query_text}")

        limit = int(body.get("limit", 30))
        
        projects = fetch_grantsgov_projects(query_text, limit=limit)
        if not projects:
            return create_success_response({
                "step": "1",
                "grants": [],
                "total_found": 0,
                "message": "No opportunities found for your keyword.",
                "query": query_text
            })
        
        print(f"Retrieved {len(projects)} opportunities.")
        
        # Return simplified grant data for step 2
        simplified_grants = []
        for i, project in enumerate(projects):
            simplified_grants.append({
                "id": i,
                "title": project.get('title', 'N/A'),
                "agency": project.get('agency', 'N/A'),
                "description": project.get('description', 'N/A'),
                "eligibility": project.get('eligibilityInformation', 'N/A'),
                "funding_instrument": project.get('fundingInstrumentType', 'N/A'),
                "category": project.get('categoryOfFundingActivity', 'N/A')
            })

        # Save the search (step 1 only)
        search_id = save_search_to_memory(query_text, simplified_grants)
        
        return create_success_response({
            "step": "1",
            "grants": simplified_grants,
            "total_found": len(projects),
            "message": f"Found {len(projects)} grants for '{query_text}'. Now provide your problem and solution descriptions.",
            "query": query_text,
            "search_id": search_id  # Include search_id for step 2
        })
        
    except Exception as e:
        return create_error_response(f"Step 1 error: {str(e)}")

def handle_step_2(body):
    """Step 2: Match grants to problem/solution using Claude"""
    print("Step 2 body:", body)
    try:
        problem_description = body.get("problem", "")
        solution_description = body.get("solution", "")
        grants = body.get("grants", [])
        search_id = body.get("search_id")  # Get search_id from step 1
        
        if not problem_description or not solution_description:
            return create_error_response("Both problem and solution descriptions are required for step 2")
        
        if not grants:
            return create_error_response("No grants data provided for matching")
        
        print(f"Step 2: Matching {len(grants)} grants to problem/solution")
        
        # Format grants for Claude analysis (limit to top 10 for better analysis)
        formatted_grants = "\n".join([
            f"{i+1}. Title: {grant.get('title')}\n"
                f"   Opportunity ID: {'id'}\n"
                f"   Agency: {grant.get('agency')} | Status: {grant.get('oppStatus')}\n"
                f"   Open: {grant.get('openDate')} — Close: {grant.get('closeDate')}\n"
            for i, grant in enumerate(grants[:30])  # Limit to 10 for better analysis
        ])
        
        prompt = f"""You are an expert grants advisor. I will provide you with:
                1. A problem description
                2. A solution description  
                3. A list of available funding opportunities

                Based on these inputs, analyze and recommend the top 3 most relevant grants.

                PROBLEM DESCRIPTION:
                {problem_description}

                SOLUTION DESCRIPTION:
                {solution_description}

                AVAILABLE FUNDING OPPORTUNITIES:
                {formatted_grants}

                Please analyze these opportunities and provide:
                1. The top 3 most relevant grants for this problem/solution
                2. For each recommendation, explain:
                - Why this grant is a good match
                - How the problem/solution aligns with the grant's goals
                - Key eligibility requirements to note
                - Any strategic advice for the application

                Format your response with clear sections for each of the 3 recommendations."""

        claude_response = query_claude(prompt, max_tokens=2000)

        # Update the saved search with step 2 data
        if search_id and hasattr(save_search_to_memory, "searches"):
            for search in save_search_to_memory.searches:
                if search["id"] == search_id:
                    search["problem_statement"] = problem_description
                    search["solution_description"] = solution_description
                    search["claude_response"] = claude_response
                    search["analysis_completed"] = True
                    break
        
        return create_success_response({
            "step": "2",
            "claude_response": claude_response,
            "total_analyzed": len(grants),
            "message": "Claude's analysis of your problem/solution match:"
        })
        
    except Exception as e:
        return create_error_response(f"Step 2 error: {str(e)}")

def create_success_response(data):
    """Helper function to create successful response"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(data)
    }

def create_error_response(error_message):
    """Helper function to create error response"""
    return {
        "statusCode": 500,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "error": error_message,
            "message": "An error occurred processing your request"
        })
    }