import json

# Test cases for your Lambda function
# Run these in the AWS Lambda console or locally

# TEST 1: Step 1 - Keyword Search
test_step1_event = {
    "body": json.dumps({
        "step": "1",
        "query": "cancer research"
    })
}

# TEST 2: Step 1 - API Gateway format
test_step1_api_gateway = {
    "httpMethod": "POST",
    "headers": {
        "Content-Type": "application/json"
    },
    "body": json.dumps({
        "step": "1",
        "query": "renewable energy"
    })
}

# TEST 3: Step 2 - Problem/Solution Analysis
test_step2_event = {
    "body": json.dumps({
        "step": "2",
        "problem": "Current cancer treatments have severe side effects and limited effectiveness for certain types of cancer. Many patients experience treatment resistance and poor quality of life.",
        "solution": "We propose to develop a novel targeted therapy using AI-designed peptides that can specifically target cancer cells while minimizing damage to healthy tissue. Our approach combines machine learning with synthetic biology.",
        "grants": [
            {
                "id": 0,
                "title": "NIH Small Business Innovation Research (SBIR)",
                "agency": "National Institutes of Health",
                "description": "The NIH SBIR program supports domestic small businesses that engage in research and development with the potential for commercialization.",
                "eligibility": "Small business concerns",
                "funding_instrument": "Grant",
                "category": "Health"
            },
            {
                "id": 1,
                "title": "NSF Innovation Corps (I-Corps)",
                "agency": "National Science Foundation",
                "description": "I-Corps prepares scientists and engineers to extend their focus beyond the laboratory to increase the economic and societal impact of NSF-funded research.",
                "eligibility": "Academic institutions",
                "funding_instrument": "Grant",
                "category": "Technology Transfer"
            }
        ]
    })
}

# TEST 4: Error case - Missing required fields
test_error_case = {
    "body": json.dumps({
        "step": "1"
        # Missing query field
    })
}

# TEST 5: Error case - Invalid step
test_invalid_step = {
    "body": json.dumps({
        "step": "3",
        "query": "test"
    })
}

# Instructions for testing:
print("=== LAMBDA FUNCTION TEST CASES ===")
print("\n1. Test Step 1 (Keyword Search):")
print("Event:", json.dumps(test_step1_event, indent=2))
print("\n2. Test Step 1 (API Gateway format):")
print("Event:", json.dumps(test_step1_api_gateway, indent=2))
print("\n3. Test Step 2 (Problem/Solution Analysis):")
print("Event:", json.dumps(test_step2_event, indent=2))
print("\n4. Test Error Case (Missing Query):")
print("Event:", json.dumps(test_error_case, indent=2))
print("\n5. Test Invalid Step:")
print("Event:", json.dumps(test_invalid_step, indent=2))

# Minimal test function to run in Lambda console
def minimal_test():
    """
    Paste this into your Lambda function for basic testing
    """
    # Test the lambda_handler function
    test_event = {
        "body": json.dumps({
            "step": "1",
            "query": "test"
        })
    }
    
    try:
        result = lambda_handler(test_event, {})
        print("Lambda test result:", result)
        return result
    except Exception as e:
        print("Lambda test error:", str(e))
        return {"error": str(e)}

# Expected responses for validation:
expected_responses = {
    "step1_success": {
        "statusCode": 200,
        "body": {
            "step": "1",
            "grants": [],  # Array of grant objects
            "total_found": 0,  # Number
            "message": "Found X grants for 'query'",
            "query": "test query"
        }
    },
    "step2_success": {
        "statusCode": 200,
        "body": {
            "step": "2",
            "claude_response": "Claude's analysis text...",
            "total_analyzed": 2,
            "message": "Claude's analysis of your problem/solution match:"
        }
    },
    "error_response": {
        "statusCode": 500,
        "body": {
            "error": "Error message",
            "message": "An error occurred processing your request"
        }
    }
}

print("\n=== EXPECTED RESPONSE FORMATS ===")
for key, response in expected_responses.items():
    print(f"\n{key}:")
    print(json.dumps(response, indent=2))