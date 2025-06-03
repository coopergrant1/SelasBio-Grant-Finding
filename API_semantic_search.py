import requests
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# =============================
# STEP 1: Query NIH RePORTER API
# =============================

def fetch_nih_projects(query_text, limit=500):
    url = "https://api.reporter.nih.gov/v2/projects/search"
    payload = {
        "criteria": {
            "advanced_text_search": {
            "operator": "or",
            "search_field": "all",
            "search_text": query_text
        }
        },
        "includeFields": ["ProjectTitle", "AbstractText", "PiNames", "OrgName"],
        "offset": 0,
        "limit": limit
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f"NIH API error: {response.status_code} - {response.text}")
    return response.json().get("results", [])

# =============================
# STEP 2: Build Text Corpus
# =============================

def build_project_text(project):
    title = project.get("project_title", "")
    abstract = project.get("abstract_text", "")
    pi = ", ".join(project.get("pi_names", []))
    org = project.get("org_name", "")
    return f"{title} | {abstract} | PI: {pi} | Org: {org}"

def build_corpus(projects):
    return [build_project_text(p) for p in projects]

# =============================
# STEP 3: Embed and Index
# =============================

def embed_corpus(corpus, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(corpus, show_progress_bar=True, batch_size=64)
    return embeddings, model

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index

# =============================
# STEP 4: Query and Search
# =============================

def search_projects(user_query, model, index, project, top_k=5):
    query_vec = model.encode([user_query])
    D, I = index.search(np.array(query_vec), k=top_k)
    return [project[i] for i in I[0]]

# =============================
# MAIN
# =============================

def main():
    api_query = input("Enter NIH grant topic to fetch: ")
    print("\n📡 Fetching grants from NIH RePORTER API...")
    projects = fetch_nih_projects(api_query)

    if not projects:
        print("No projects found.")
        return

    print(f"✅ Fetched {len(projects)} projects.")

    corpus = build_corpus(projects)
    embeddings, model = embed_corpus(corpus)
    index = build_faiss_index(embeddings)

    while True:
        user_query = input("\n🔎 Enter a funding need (or 'exit'): ")
        if user_query.lower() in ("exit", "quit"):
            break

        results = search_projects(user_query, model, index, projects)
        print("\nTop Matches:")
        for i, proj in enumerate(results):
            title = proj.get("project_title", "N/A")
            abstract = proj.get("abstract_text", "N/A")
            fiscal_year = proj.get("fiscal_year", "N/A")

            pi_list = proj.get("principal_investigators", [])
            pi_names = ", ".join(f"{pi.get('first_name', '')} {pi.get('last_name', '')}".strip() for pi in pi_list) or "N/A"

            org = proj.get("organization", {}).get("org_name", "N/A")

            print(f"\n{i+1}. Title: {title}\n   Abstract: {abstract[:300]}...\n   PI(s): {pi_names}\n   Org: {org}\n   Fiscal Year: {fiscal_year}")

if __name__ == "__main__":
    main()
