import os
from dotenv import load_dotenv
import chromadb
from google import genai

load_dotenv()

# Initialize API and clients
google_api = os.getenv("GEMINI_API_KEY")
genai_client = genai.Client(api_key=google_api)

chroma_client = chromadb.PersistentClient(path="../data/embeddings")
collection_name = "document_collection"
collection = chroma_client.get_or_create_collection(name=collection_name)


def query_documents(question, n_results=5):
    """Query the vector database for relevant document chunks."""
    try:
        results = collection.query(
            query_texts=[question],
            n_results=n_results
        )
        
        relevant_chunks = []
        
        if results.get("documents"):
            for doc_list in results["documents"]:
                relevant_chunks.extend(doc_list)
        
        return relevant_chunks
    
    except Exception as e:
        print(f"Error querying documents: {e}")
        return []


def generate_response(question, relevant_chunks):
    """Generate a response using retrieved context and Gemini."""
    if not relevant_chunks:
        return "I don't have enough information to answer this question."
    
    context = "\n\n".join(relevant_chunks)
    
    prompt = (
        "You are an assistant for Thailand Tax deduction. Use the following pieces of "
        "retrieved context to calculate the total deduction. If you don't know the answer, "
        "say that you don't know. Use three sentences maximum and keep the answer concise."
        f"\n\nContext:\n{context}\n\nQuestion:\n{question}"
    )
    
    try:
        response = genai_client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )
        
        return response.text
    
    except Exception as e:
        print(f"Error generating response: {e}")
        return "An error occurred while generating the response."


def ask_question(question):
    """Main function to ask a question and get an answer."""
    print(f"Question: {question}")
    
    relevant_chunks = query_documents(question)
    
    if not relevant_chunks:
        return "No relevant information found in the database."
    
    print(f"Found {len(relevant_chunks)} relevant chunks")
    
    answer = generate_response(question, relevant_chunks)
    
    return answer