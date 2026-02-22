"""Workflow orchestration for the tax assistant multi-agent system."""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from app.agents.inspector import extract_receipt_json
from app.agents.tax_expert import ask_tax_expert, ask_tax_question
from app.agents.accountant import save_receipt_from_inspector


class AgentState(TypedDict):
    """State for the tax assistant workflow."""
    question: str
    image_path: str
    receipt_data: dict
    tax_analysis: dict
    tax_advice: str
    needs_human_input: bool
    missing_fields: list
    status: str
    accountant_result: dict
    user_id: str
    messages: Annotated[list, add_messages]


# ---------------------------------------------------------------------------
# Entry-point router
# ---------------------------------------------------------------------------

def should_inspect_receipt(state: AgentState) -> str:
    """Decide if we need to inspect a receipt image."""
    if state.get("image_path"):
        return "inspect"
    return "tax_question"


# ---------------------------------------------------------------------------
# Node 1: Inspector (OCR only)
# ---------------------------------------------------------------------------

def inspect_receipt_node(state: AgentState) -> AgentState:
    """Extract raw data from receipt image via Gemini Vision."""
    print("Node 1: Inspector Agent - Analyzing receipt...")

    image_path = state["image_path"]
    receipt_data = extract_receipt_json(image_path)

    state["receipt_data"] = receipt_data
    state["messages"].append({
        "role": "system",
        "content": f"Receipt extracted: {receipt_data}"
    })

    print(f"Extracted: date={receipt_data.get('date')}, "
          f"amount={receipt_data.get('amount')}, "
          f"tax_id={receipt_data.get('tax_id')}")

    return state


# ---------------------------------------------------------------------------
# Node 2: Validator (conditional edge function)
# ---------------------------------------------------------------------------

def validate_receipt_data(state: AgentState) -> str:
    """Check if receipt data is complete before proceeding."""
    receipt_data = state.get("receipt_data", {})

    if receipt_data.get("error"):
        print("Validation: Receipt has extraction error -> Human input needed")
        return "human_input"

    date = receipt_data.get("date")
    amount = receipt_data.get("amount")
    tax_id = receipt_data.get("tax_id")

    if date and amount and tax_id:
        print("Validation: Data complete -> Proceed to Tax Expert")
        return "tax_expert"

    missing = []
    if not date:
        missing.append("date")
    if not amount:
        missing.append("amount")
    if not tax_id:
        missing.append("tax_id")

    print(f"Validation: Missing fields: {', '.join(missing)} -> Human input needed")
    return "human_input"


# ---------------------------------------------------------------------------
# Node 3: Tax Expert (RAG classification)
# ---------------------------------------------------------------------------

def tax_expert_node(state: AgentState) -> AgentState:
    """Classify receipt via RAG and store structured result."""
    print("Node 3: Tax Expert Agent - Classifying receipt...")

    receipt_data = state["receipt_data"]
    tax_analysis = ask_tax_expert(receipt_data)

    state["tax_analysis"] = tax_analysis
    state["messages"].append({
        "role": "system",
        "content": f"Tax analysis: {tax_analysis}"
    })

    print(f"Tax Expert result: is_deductible={tax_analysis.get('is_deductible')}, "
          f"category={tax_analysis.get('category')}")

    return state


# ---------------------------------------------------------------------------
# Node 4: Accountant (save to DB)
# ---------------------------------------------------------------------------

def accountant_node(state: AgentState) -> AgentState:
    """Save transaction to database using receipt data + tax analysis."""
    print("Node 4: Accountant Agent - Saving transaction...")

    receipt_data = state["receipt_data"]
    tax_analysis = state.get("tax_analysis", {})
    user_id = state.get("user_id", "demo-user-id")

    final_category = tax_analysis.get("category", "None")
    print(f"Saving with category: {final_category}")

    result = save_receipt_from_inspector(
        user_id=user_id,
        receipt_data=receipt_data,
        category_name=final_category,
        tax_result=tax_analysis,
    )

    state["accountant_result"] = result
    state["status"] = "completed"

    if result.get("success"):
        transaction = result.get("transaction", {})
        deductible = transaction.get("deductible_amount", 0)
        print(f"Transaction saved! Deductible: {deductible} THB")
        state["messages"].append({
            "role": "system",
            "content": f"Transaction saved. Deductible: {deductible} THB"
        })
    else:
        error_msg = result.get("error", "Unknown error")
        print(f"Failed to save transaction: {error_msg}")
        state["messages"].append({
            "role": "system",
            "content": f"Error saving transaction: {error_msg}"
        })

    return state


# ---------------------------------------------------------------------------
# Human-in-the-loop node
# ---------------------------------------------------------------------------

def human_input_node(state: AgentState) -> AgentState:
    """Flag incomplete data so the API can return a form request."""
    print("Human-in-the-loop: Incomplete receipt data detected")

    receipt_data = state.get("receipt_data", {})
    missing = []

    if not receipt_data.get("date"):
        missing.append("date")
    if not receipt_data.get("amount"):
        missing.append("amount")
    if not receipt_data.get("tax_id"):
        missing.append("tax_id")

    state["needs_human_input"] = True
    state["missing_fields"] = missing
    state["status"] = "awaiting_user_input"
    state["messages"].append({
        "role": "system",
        "content": f"Missing fields: {', '.join(missing)}. Awaiting user input."
    })

    print(f"Status set to awaiting_user_input. Missing: {', '.join(missing)}")

    return state


# ---------------------------------------------------------------------------
# Tax Q&A node (no receipt, free-text question only)
# ---------------------------------------------------------------------------

def tax_question_node(state: AgentState) -> AgentState:
    """Answer a free-text tax question using RAG."""
    print("Tax Q&A: Answering question...")

    question = state.get("question", "")
    answer = ask_tax_question(question)

    state["tax_advice"] = answer
    state["status"] = "completed"
    state["messages"].append({
        "role": "assistant",
        "content": answer,
    })

    return state


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_workflow():
    """Build the LangGraph workflow.

    Flow:
    START -> Router (has image?)
          -> Inspector -> Validator (data complete?)
                       -> Tax Expert (RAG) -> Accountant (DB) -> END
                       -> Human Input (if incomplete) -> END
          -> Tax Q&A (if no image, free-text question) -> END
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("inspect", inspect_receipt_node)
    workflow.add_node("tax_expert", tax_expert_node)
    workflow.add_node("accountant", accountant_node)
    workflow.add_node("human_input", human_input_node)
    workflow.add_node("tax_question", tax_question_node)

    # Entry point: decide receipt vs question
    workflow.set_conditional_entry_point(
        should_inspect_receipt,
        {
            "inspect": "inspect",
            "tax_question": "tax_question",
        }
    )

    # After Inspector, validate completeness
    workflow.add_conditional_edges(
        "inspect",
        validate_receipt_data,
        {
            "tax_expert": "tax_expert",
            "human_input": "human_input",
        }
    )

    # After Tax Expert, save to DB
    workflow.add_edge("tax_expert", "accountant")

    # Terminal nodes
    workflow.add_edge("accountant", END)
    workflow.add_edge("human_input", END)
    workflow.add_edge("tax_question", END)

    return workflow.compile()


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_tax_assistant(question: str, image_path: str = None, user_id: str = "demo-user-id"):
    """Run the tax assistant workflow."""
    print("=" * 60)
    print("TicTaxFlow AI Assistant")
    print("=" * 60)

    initial_state = {
        "question": question,
        "image_path": image_path,
        "receipt_data": {},
        "tax_analysis": {},
        "tax_advice": "",
        "needs_human_input": False,
        "missing_fields": [],
        "status": "",
        "accountant_result": {},
        "user_id": user_id,
        "messages": [{"role": "user", "content": question}],
    }

    app = build_workflow()
    result = app.invoke(initial_state)

    print("\n" + "=" * 60)
    print("Result:")
    print("=" * 60)

    if result.get("receipt_data"):
        print("\nReceipt Data:")
        for key, value in result["receipt_data"].items():
            print(f"  {key}: {value}")

    if result.get("tax_analysis"):
        print(f"\nTax Analysis: {result['tax_analysis']}")

    if result.get("accountant_result"):
        accountant_result = result["accountant_result"]
        if accountant_result.get("success"):
            print("\nTransaction Saved:")
            transaction = accountant_result.get("transaction", {})
            print(f"  ID: {transaction.get('id', 'N/A')}")
            print(f"  Amount: {transaction.get('total_amount', 0)} THB")
            print(f"  Deductible: {transaction.get('deductible_amount', 0)} THB")
            print(f"  Status: {transaction.get('status', 'N/A')}")
        else:
            print(f"\nTransaction Error: {accountant_result.get('error', 'Unknown')}")

    if result.get("status") == "awaiting_user_input":
        print(f"\nStatus: Awaiting user input")
        print(f"Missing fields: {result.get('missing_fields', [])}")
    elif result.get("tax_advice"):
        print(f"\nTax Advice:\n{result['tax_advice']}")

    print(f"\nFinal status: {result.get('status', 'N/A')}")
    print("=" * 60)

    return result


def main():
    """Test the workflow."""
    from app.core.config import settings

    print("LangGraph Workflow - Tax Assistant")
    print("\nExample 1: Question only")
    print("-" * 60)

    result1 = run_tax_assistant("Easy E-Receipt deduction limit?")

    print("\n\nExample 2: Question with receipt (if available)")
    print("-" * 60)

    test_image = settings.RECEIPTS_DIR / "sample_receipt.jpg"
    if test_image.exists():
        result2 = run_tax_assistant(
            "Can I use this receipt for tax deduction?",
            image_path=str(test_image),
        )
    else:
        print("No test receipt found. Place an image at:")
        print(f"  {test_image}")

    print("\nWorkflow ready!")


if __name__ == "__main__":
    main()
