from app.knowledge.retrieval import retrieve_relevant_knowledge
import json

def test_rag_retrieval():
    query = "What are the prerequisites for the advanced Python course?"
    print(f"Retrieving relevant knowledge for query: \"{query}\"")
    
    relevant_docs = retrieve_relevant_knowledge(query)
    
    if relevant_docs:
        print(f"Successfully retrieved {len(relevant_docs)} documents.")
        for doc in relevant_docs:
            print(json.dumps(doc, indent=2))
    else:
        print("No relevant documents found or an error occurred during retrieval.")

if __name__ == "__main__":
    test_rag_retrieval()