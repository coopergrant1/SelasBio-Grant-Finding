import requests
import json

url = "https://api.reporter.nih.gov/v2/projects/search"

payload = {
    "criteria": {
        "text": "diabetes"
    },
    "include_fields": [
        "project_title",
        "principal_investigators.full_name",
        "organization.org_name",
        "fiscal_year"
    ],
    "offset": 0,
    "limit": 5
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    data = response.json()
    if not data.get("results") or data["results"] == [{}] * len(data["results"]):
        print("No usable data returned.")
        print(json.dumps(data, indent=2))
    else:
        for project in data["results"]:
            title = project.get("project_title", "N/A")
            fiscal_year = project.get("fiscal_year", "N/A")
            pi_list = project.get("principal_investigators", [])
            pi_name = pi_list[0].get("full_name", "N/A") if pi_list else "N/A"
            org = project.get("organization", {})
            org_name = org.get("org_name", "N/A")
            
            print(f"Title: {title}")
            print(f"PI: {pi_name}")
            print(f"Organization: {org_name}")
            print(f"Fiscal Year: {fiscal_year}\n")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
