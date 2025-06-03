import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# =============================
# STEP 1: Load and Clean Data
# =============================

def load_cleaned_grants(file_path):
    df = pd.read_csv(file_path)
    return df

# =============================
# STEP 2: Build Text for Embedding
# =============================

def build_text(row):
    parts = [
        row.get("project_title", ""),
        row.get("project_terms", ""),
        row.get("org_name", ""),
        row.get("org_state", ""),
        row.get("pi_names", "")
    ]
    return " | ".join([str(p) for p in parts if p])

def build_corpus(df):
    return df.apply(build_text, axis=1).tolist()

# =============================
# STEP 3: Generate Embeddings
# =============================

def embed_corpus(corpus, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    # embeddings = model.encode(corpus, show_progress_bar=True, batch_size=64)
    # np.save("grant_embeddings.npy", embeddings)
    embeddings = np.load("grant_embeddings.npy")
    return embeddings, model

# =============================
# STEP 4: Build and Use FAISS Index
# =============================

def build_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    return index

def search_faiss(query, model, index, df, top_k=5):
    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec), k=top_k)
    results = []
    for idx in I[0]:
        row = df.iloc[idx].to_dict()
        results.append({
            "title": row.get("project_title", "N/A"),
            "terms": str(row.get("project_terms", "N/A") or "N/A"),
            "org": row.get("org_name", ""),
            "location": row.get("org_state", ""),
            "pi": row.get("pi_names", "")
        })
    return results

# =============================
# MAIN (example usage)
# =============================

def main():
    df = load_cleaned_grants("cleaned_grants.csv")
    corpus = build_corpus(df)
    embeddings, model = embed_corpus(corpus)
    index = build_faiss_index(embeddings)

    print("\n🔎 Enter a query to search grants (type 'exit' to quit):")
    while True:
        query = input("\nYour query: ")
        if query.lower() in ["exit", "quit"]:
            break

        results = search_faiss(query, model, index, df)
        for i, r in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"Title: {r['title']}")
            print(f"Org: {r['org']} ({r['location']})")
            print(f"PI: {r['pi']}")
            print(f"Keywords: {r['terms'][:200]}...")

if __name__ == "__main__":
    main()
