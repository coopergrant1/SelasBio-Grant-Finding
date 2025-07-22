import requests

def fetch_grantsgov_projects(query_text, limit = 5):
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

def main():
    api_query = "cancer"
    projects = fetch_grantsgov_projects(api_query)
    for i, proj in enumerate(projects, 1):
            opportunity_id = proj.get("id")
            print(
                f"\n{i}. Title: {proj.get('title')}\n"
                f"   Opportunity ID: {opportunity_id}\n"
                f"   Agency: {proj.get('agency')} | Status: {proj.get('oppStatus')}\n"
                f"   Open: {proj.get('openDate')} — Close: {proj.get('closeDate')}\n"
                # f"   Summary: {synopsis[:1000]}..."
            )

if __name__ == "__main__":
    main()
