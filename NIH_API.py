import requests

url = "https://api.reporter.nih.gov/v2/publications/search"

payload = {
    "criteria": {
        "advanced_text_search": {
            "operator": "or",
            "search_field": "all",
            "search_text": "cancer"
        }
    },
    "include_fields": [
        "ProjectTitle",
        "AbstractText",
        "PrincipalInvestigators",
        "Organization",
        "FiscalYear"
    ],
    "offset": 0,
    "limit": 5
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    data = response.json()
    print(data)
    for project in data.get("results", []):
        title = project.get("project_title", "N/A")
        abstract = project.get("abstract_text", "N/A")
        fiscal_year = project.get("fiscal_year", "N/A")

        # Extract principal investigator names
        pi_list = project.get("principal_investigators", [])
        pi_names = ", ".join(f"{pi.get('first_name', '')} {pi.get('last_name', '')}".strip() for pi in pi_list) if pi_list else "N/A"

        # Extract organization name
        org = project.get("organization", {}).get("org_name", "N/A")

        print(f"Title: {title}")
        print(f"Abstract: {abstract}")
        print(f"Principal Investigator(s): {pi_names}")
        print(f"Organization: {org}")
        print(f"Fiscal Year: {fiscal_year}\n")
else:
    print(f"Request failed with status code {response.status_code}")
