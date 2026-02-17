"""RAG (Retrieval-Augmented Generation) service for querying documents."""
import chromadb
from google import genai

from app.core.config import settings


genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

chroma_client = chromadb.PersistentClient(path=str(settings.EMBEDDINGS_DIR))
collection_name = settings.CHROMA_COLLECTION_NAME
collection = chroma_client.get_or_create_collection(name=collection_name)


def query_documents(question, n_results=None):
    """Query the vector database for relevant document chunks."""
    if n_results is None:
        n_results = settings.RAG_N_RESULTS
        
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
            model=f"models/{settings.GEMINI_MODEL}",
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
