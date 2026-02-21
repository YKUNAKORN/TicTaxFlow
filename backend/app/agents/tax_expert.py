"""Tax Expert Agent for analyzing receipt deductibility using RAG."""
import json
from typing import Dict, Any

import chromadb
from google import genai

from app.core.config import settings


genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

chroma_client = chromadb.PersistentClient(path=str(settings.EMBEDDINGS_DIR))
collection = chroma_client.get_or_create_collection(name=settings.CHROMA_COLLECTION_NAME)

DEFAULT_RESULT: Dict[str, Any] = {
    "is_deductible": False,
    "category": "None",
    "reasoning": "",
}


def retrieve_context(query: str, n_results: int = None) -> list:
    """Retrieve relevant context from vector database."""
    if n_results is None:
        n_results = settings.RAG_N_RESULTS

    try:
        results = collection.query(
            query_texts=[query],
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


def build_tax_expert_prompt(receipt_data: Dict[str, Any], context: str) -> str:
    """Build a prompt that forces Gemini to return ONLY a JSON object.

    The prompt instructs the model to classify the receipt against
    Thai tax deduction rules retrieved from ChromaDB.
    """
    prompt = f"""You are a Thai tax deduction classifier.
Analyze the receipt data below against the provided tax rules context and determine its deductibility.

Receipt Data:
- Date: {receipt_data.get("date", "N/A")}
- Amount: {receipt_data.get("amount", "N/A")}
- Merchant: {receipt_data.get("merchant_name", "N/A")}

Tax Rules Context:
{context}

Respond with ONLY a valid JSON object using this exact schema (no markdown, no code fences, no extra text):
{{"is_deductible": true or false, "category": "one of the categories below or None", "reasoning": "brief explanation"}}

Valid categories: "Easy E-Receipt", "Thai ESG", "Life Insurance", "Health Insurance", "Pension Insurance", "Social Security", "Provident Fund", "SSF", "RMF", "Home Loan Interest", "Donation (General)", "Donation (Education/Sports)", "None"

Rules:
- Set is_deductible to true only if the receipt clearly qualifies under a Thai tax deduction category.
- Set category to "None" if the receipt does not qualify for any deduction.
- Keep reasoning under 2 sentences."""

    return prompt


def _parse_json_response(raw_text: str) -> Dict[str, Any]:
    """Parse a JSON object from Gemini's raw text response."""
    text = raw_text.strip()

    # Strip markdown code fences if the model included them
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    result = json.loads(text)

    return {
        "is_deductible": result.get("is_deductible", False),
        "category": result.get("category", "None"),
        "reasoning": result.get("reasoning", "No reasoning provided."),
    }


def ask_tax_expert(receipt_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze receipt data for tax deductibility using RAG.

    Args:
        receipt_data: Dict with receipt fields (date, amount, merchant_name).

    Returns:
        Dict with keys: is_deductible (bool), category (str), reasoning (str).
    """
    merchant = receipt_data.get("merchant_name", "")
    amount = receipt_data.get("amount", "")
    date = receipt_data.get("date", "")

    query = f"tax deduction {merchant} {amount} {date}"
    print(f"Tax Expert RAG query: {query}")

    context_chunks = retrieve_context(query)

    if not context_chunks:
        return {
            **DEFAULT_RESULT,
            "reasoning": "No relevant tax rules found in the knowledge base.",
        }

    print(f"Found {len(context_chunks)} relevant documents")

    context = "\n\n".join(context_chunks)
    prompt = build_tax_expert_prompt(receipt_data, context)

    try:
        response = genai_client.models.generate_content(
            model=f"models/{settings.GEMINI_MODEL}",
            contents=prompt,
        )

        return _parse_json_response(response.text)

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from Gemini response: {e}")
        print(f"Raw response: {response.text}")
        return {
            **DEFAULT_RESULT,
            "reasoning": "Failed to parse tax analysis response.",
        }
    except Exception as e:
        print(f"Error generating response: {e}")
        return {
            **DEFAULT_RESULT,
            "reasoning": "An error occurred during tax analysis.",
        }


def ask_tax_question(question: str) -> str:
    """Answer a free-text tax question using RAG (conversational mode).

    This is used by the chat endpoint for general tax Q&A.
    """
    print(f"Tax Expert question: {question}")

    context_chunks = retrieve_context(question)

    if not context_chunks:
        return "No relevant information found in the knowledge base."

    print(f"Found {len(context_chunks)} relevant documents")
    context = "\n\n".join(context_chunks)

    prompt = f"""You are a Thai Tax Expert. Answer the question based on the context.

Context:
{context}

Question: {question}

Instructions:
- Answer in the same language as the question (Thai or English).
- Be precise with numbers and amounts.
- Use bullet points and bold for readability.

Answer:"""

    try:
        response = genai_client.models.generate_content(
            model=f"models/{settings.GEMINI_MODEL}",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "An error occurred while generating the response."


def main():
    """Test the tax expert agent."""
    test_receipt = {
        "date": "2026-01-15",
        "amount": 5000,
        "merchant_name": "Bangkok Hospital",
    }

    print("Tax Expert Agent - Structured Analysis")
    print("=" * 60)
    print(f"Receipt: {test_receipt}")
    result = ask_tax_expert(test_receipt)
    print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
