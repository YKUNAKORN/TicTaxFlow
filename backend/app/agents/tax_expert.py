"""Tax Expert Agent for analyzing receipt deductibility using RAG."""
import json
import time
from datetime import datetime
from typing import Dict, Any

import chromadb
from google import genai

from app.core.config import settings

MAX_RETRIES = 3
RETRY_BASE_DELAY = 3  # seconds


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
    Thai tax deduction rules using both RAG context and base knowledge.
    """
    ce_year = settings.DEFAULT_TAX_YEAR
    be_year = ce_year + 543

    prompt = f"""You are a Thai tax deduction classifier.
Analyze the receipt data below and determine its deductibility.

Receipt Data:
- Date: {receipt_data.get("date", "N/A")}
- Amount: {receipt_data.get("amount", "N/A")}
- Merchant: {receipt_data.get("merchant_name", "N/A")}

IMPORTANT:
- The receipt was uploaded as a scanned document. Assume it is a valid e-Tax Invoice or e-Receipt.
- The current tax year is {ce_year} CE / BE {be_year}.

--- Base Knowledge: Thai Tax Deduction Categories (Tax Year {ce_year} / BE {be_year}) ---

YEAR-ROUND deductions (valid any date within the tax year):
1. Life Insurance: Premiums for life insurance (10+ year policy). Max 100,000 THB.
2. Health Insurance: Premiums for health insurance for self. Max 25,000 THB.
   Combined with life insurance must not exceed 100,000 THB.
3. Parent Health Insurance: Health insurance premiums for parents. Max 15,000 THB.
4. Pension Insurance: Retirement mutual fund insurance premiums. Max 200,000 THB.
5. Social Security: Employee contributions. Max 9,000 THB.
6. Provident Fund: Employee contributions. Max 10,000 THB (excess up to 490,000 capped).
7. SSF (Super Savings Fund): Max 30% of income, up to 200,000 THB.
8. RMF (Retirement Mutual Fund): Max 30% of income, up to 500,000 THB.
9. Thai ESG Fund: Max 30% of income, up to 300,000 THB.
10. Home Loan Interest: Max 100,000 THB.
11. Donation (General): Actual amount paid, max 10% of income after deductions.
12. Donation (Education/Sports): 2x actual amount paid via e-Donation.

TIME-LIMITED deductions:
13. Easy E-Receipt 2.0: Purchases with e-Tax Invoice/e-Receipt.
    Period: Jan 16 - Feb 28 of the tax year. Max 50,000 THB.

--- Retrieved Tax Rules Context (from knowledge base) ---
{context}

Respond with ONLY a valid JSON object using this exact schema (no markdown, no code fences, no extra text):
{{"is_deductible": true or false, "category": "one of the categories below or None", "reasoning": "brief explanation"}}

Valid categories: "Easy E-Receipt", "Thai ESG", "Life Insurance", "Health Insurance", "Pension Insurance", "Social Security", "Provident Fund", "SSF", "RMF", "Home Loan Interest", "Donation (General)", "Donation (Education/Sports)", "None"

Rules:
- Classify based on merchant name, amount, and date against the categories above.
- For Easy E-Receipt, verify the receipt date falls within Jan 16 - Feb 28 of the current tax year.
- For insurance (health, life, pension), the receipt is deductible if the date is within the tax year. These are NOT time-limited.
- For donations, identify from merchant name (e.g. foundations, temples, charities). These are NOT time-limited.
- Set is_deductible to true if the receipt plausibly qualifies under any category.
- Set category to "None" only if the receipt clearly does not match any deduction category.
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

    Uses multiple RAG queries to retrieve both merchant-specific and
    category-level tax rules from the knowledge base.

    Args:
        receipt_data: Dict with receipt fields (date, amount, merchant_name).

    Returns:
        Dict with keys: is_deductible (bool), category (str), reasoning (str).
    """
    merchant = receipt_data.get("merchant_name", "")
    amount = receipt_data.get("amount", "")
    date = receipt_data.get("date", "")

    # Build multiple queries to cover different angles of the knowledge base
    queries = [
        f"หักลดหย่อน {merchant}",
        f"ค่าลดหย่อนภาษี tax deduction categories {date}",
    ]

    # Add domain-specific query based on merchant name keywords
    merchant_lower = merchant.lower()
    if any(kw in merchant_lower for kw in ["มูลนิธิ", "บริจาค", "donation", "สภากาชาด", "foundation", "วัด", "temple", "charity"]):
        queries.append("เงินบริจาค donation หักลดหย่อน การศึกษา กีฬา e-Donation")
    elif any(kw in merchant_lower for kw in ["ประกัน", "insurance", "สุขภาพ", "ชีวิต", "premium"]):
        queries.append("เบี้ยประกันสุขภาพ เบี้ยประกันชีวิต หักลดหย่อน health life insurance")
    elif any(kw in merchant_lower for kw in ["กองทุน", "fund", "ssf", "rmf", "esg"]):
        queries.append("กองทุน SSF RMF Thai ESG หักลดหย่อน")
    elif any(kw in merchant_lower for kw in ["ประกันสังคม", "สปส", "sso", "social security"]):
        queries.append("ประกันสังคม เงินสมทบ หักลดหย่อน social security")
    else:
        queries.append("Easy E-Receipt ใบกำกับภาษีอิเล็กทรอนิกส์ e-Tax Invoice ซื้อสินค้า")

    print(f"Tax Expert RAG queries: {queries}")

    # Retrieve context from all queries and deduplicate
    all_chunks = []
    seen = set()
    for q in queries:
        chunks = retrieve_context(q, n_results=3)
        for chunk in chunks:
            chunk_key = chunk[:100]
            if chunk_key not in seen:
                seen.add(chunk_key)
                all_chunks.append(chunk)

    if not all_chunks:
        return {
            **DEFAULT_RESULT,
            "reasoning": "No relevant tax rules found in the knowledge base.",
        }

    print(f"Found {len(all_chunks)} unique context chunks")

    context = "\n\n".join(all_chunks)
    prompt = build_tax_expert_prompt(receipt_data, context)

    for attempt in range(MAX_RETRIES):
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
            if "429" in str(e) and attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                print(f"Rate limited, retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(delay)
                continue
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
