import os
from dotenv import load_dotenv
import chromadb
from google import genai

load_dotenv()

# Initialize clients
google_api = os.getenv("GEMINI_API_KEY")
genai_client = genai.Client(api_key=google_api)

chroma_client = chromadb.PersistentClient(path="../data/embeddings")
collection = chroma_client.get_or_create_collection(name="document_collection")


def retrieve_context(question, n_results=5):
    """Retrieve relevant context from vector database."""
    try:
        results = collection.query(
            query_texts=[question],
            n_results=n_results
        )
        
        if results.get("documents"):
            chunks = []
            for doc_list in results["documents"]:
                chunks.extend(doc_list)
            return chunks
        
        return []
    
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return []


def build_tax_expert_prompt(question, context):
    """Build a specialized prompt for Thai tax expert."""
    prompt = f"""You are a Thai Tax Expert specializing in personal income tax deductions.

Your role:
- Answer questions about Thai tax deductions accurately based on the provided context
- Explain deduction limits, rates, and conditions clearly
- Use specific numbers and amounts when available
- If information is not in the context, clearly state that you don't know

Context from tax documents:
{context}

Question: {question}

Instructions:
- Answer in the same language as the question (Thai or English)
- Be precise with numbers and amounts
- Keep answer concise but complete
- If there are multiple conditions, list them clearly

Answer:"""
    
    return prompt


def ask_tax_expert(question):
    """Ask the tax expert agent a question."""
    print(f"Question: {question}")
    
    # Retrieve relevant context
    context_chunks = retrieve_context(question)
    
    if not context_chunks:
        return "ไม่พบข้อมูลที่เกี่ยวข้องในฐานข้อมูล / No relevant information found in the database."
    
    print(f"Found {len(context_chunks)} relevant documents")
    
    # Combine context
    context = "\n\n".join(context_chunks)
    
    # Build prompt
    prompt = build_tax_expert_prompt(question, context)
    
    # Generate response
    try:
        response = genai_client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )
        
        return response.text
    
    except Exception as e:
        print(f"Error generating response: {e}")
        return "เกิดข้อผิดพลาดในการสร้างคำตอบ / An error occurred while generating the response."


def main():
    """Test the tax expert agent."""
    test_questions = [
        "ประกันชีวิตลดหย่อนได้เท่าไหร่?",
        "What is the maximum deduction for SSF?",
        "Easy E-Receipt ลดหย่อนได้สูงสุดเท่าไหร่?"
    ]
    
    print("Thai Tax Expert Agent")
    print("=" * 60)
    
    for question in test_questions:
        print(f"\nQ: {question}")
        answer = ask_tax_expert(question)
        print(f"A: {answer}")
        print("-" * 60)


if __name__ == "__main__":
    main()
