"""Workflow orchestration for the tax assistant multi-agent system."""
import logging
from typing import TypedDict, Annotated, Optional

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from app.agents.inspector import extract_receipt_json, extract_receipt_from_bytes
from app.agents.tax_expert import ask_tax_expert, ask_tax_question
from app.agents.accountant import save_receipt_from_inspector
from app.services.income_aggregator import aggregate_income
from app.services.tax_estimator import estimate_pit

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the tax assistant workflow."""
    question: str
    image_path: str
    image_bytes: bytes
    image_url: str
    receipt_data: dict
    tax_analysis: dict
    tax_advice: str
    needs_human_input: bool
    missing_fields: list
    status: str
    accountant_result: dict
    user_id: str
    seller_id: str
    period: str
    income_data: dict
    tax_estimate: dict
    messages: Annotated[list, add_messages]


# ---------------------------------------------------------------------------
# Entry-point router
# ---------------------------------------------------------------------------

def should_inspect_receipt(state: AgentState) -> str:
    """Decide the entry path: income sync, receipt image, or free-text
    question."""
    if state.get("seller_id") and state.get("period"):
        return "income"
    if state.get("image_path") or state.get("image_bytes"):
        return "inspect"
    return "tax_question"


# ---------------------------------------------------------------------------
# Node 1: Inspector (OCR only)
# ---------------------------------------------------------------------------

def inspect_receipt_node(state: AgentState) -> AgentState:
    """Extract raw data from receipt image via Gemini Vision."""
    logger.info("Node 1: Inspector - analyzing receipt")

    image_bytes = state.get("image_bytes")
    if image_bytes:
        receipt_data = extract_receipt_from_bytes(image_bytes)
    else:
        receipt_data = extract_receipt_json(state["image_path"])

    state["receipt_data"] = receipt_data
    state["messages"].append({
        "role": "system",
        "content": f"Receipt extracted: {receipt_data}"
    })

    logger.info(
        "Node 1: Inspector - extracted date=%s amount=%s tax_id=%s",
        receipt_data.get("date"), receipt_data.get("amount"), receipt_data.get("tax_id"),
    )

    return state


# ---------------------------------------------------------------------------
# Node 2: Validator (conditional edge function)
# ---------------------------------------------------------------------------

def validate_receipt_data(state: AgentState) -> str:
    """Check if receipt data is complete before proceeding."""
    receipt_data = state.get("receipt_data", {})

    if receipt_data.get("error"):
        logger.info("Node 2: Validator - extraction error, routing to human_input")
        return "human_input"

    date = receipt_data.get("date")
    amount = receipt_data.get("amount")
    tax_id = receipt_data.get("tax_id")

    if date and amount and tax_id:
        logger.info("Node 2: Validator - data complete, routing to tax_expert")
        return "tax_expert"

    missing = []
    if not date:
        missing.append("date")
    if not amount:
        missing.append("amount")
    if not tax_id:
        missing.append("tax_id")

    logger.info("Node 2: Validator - missing fields %s, routing to human_input", missing)
    return "human_input"


# ---------------------------------------------------------------------------
# Node 3: Tax Expert (RAG classification)
# ---------------------------------------------------------------------------

def tax_expert_node(state: AgentState) -> AgentState:
    """Classify receipt via RAG and store structured result."""
    logger.info("Node 3: Tax Expert - classifying receipt")

    receipt_data = state["receipt_data"]
    tax_analysis = ask_tax_expert(receipt_data)

    state["tax_analysis"] = tax_analysis
    state["messages"].append({
        "role": "system",
        "content": f"Tax analysis: {tax_analysis}"
    })

    logger.info(
        "Node 3: Tax Expert - is_deductible=%s category=%s",
        tax_analysis.get("is_deductible"), tax_analysis.get("category"),
    )

    return state


# ---------------------------------------------------------------------------
# Node 4: Accountant (save to DB)
# ---------------------------------------------------------------------------

def accountant_node(state: AgentState) -> AgentState:
    """Save transaction to database using receipt data + tax analysis."""
    logger.info("Node 4: Accountant - saving transaction")

    receipt_data = state["receipt_data"]
    tax_analysis = state.get("tax_analysis", {})
    user_id = state.get("user_id", "demo-user-id")

    final_category = tax_analysis.get("category", "None")
    logger.info("Node 4: Accountant - saving with category=%s", final_category)

    result = save_receipt_from_inspector(
        user_id=user_id,
        receipt_data=receipt_data,
        category_name=final_category,
        receipt_image_url=state.get("image_url"),
        tax_result=tax_analysis,
    )

    state["accountant_result"] = result
    state["status"] = "completed"

    if result.get("success"):
        transaction = result.get("transaction", {})
        deductible = transaction.get("deductible_amount", 0)
        logger.info("Node 4: Accountant - transaction saved, deductible=%s THB", deductible)
        state["messages"].append({
            "role": "system",
            "content": f"Transaction saved. Deductible: {deductible} THB"
        })
    else:
        error_msg = result.get("error", "Unknown error")
        logger.warning("Node 4: Accountant - failed to save transaction: %s", error_msg)
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
    logger.info("Node: Human Input - incomplete receipt data detected")

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

    logger.info("Node: Human Input - status=awaiting_user_input missing=%s", missing)

    return state


# ---------------------------------------------------------------------------
# Income path: aggregate sales, then estimate PIT
# ---------------------------------------------------------------------------

def income_node(state: AgentState) -> AgentState:
    """Aggregate multi-platform sales (seeded mock providers) for the
    synced seller/period."""
    logger.info("Node: Income - aggregating seller=%s period=%s", state["seller_id"], state["period"])

    state["income_data"] = aggregate_income(state["seller_id"], state["period"])
    state["messages"].append({
        "role": "system",
        "content": f"Income aggregated for period {state['period']}",
    })

    return state


def estimate_tax_node(state: AgentState) -> AgentState:
    """Estimate PIT due on the aggregated income's net total."""
    logger.info("Node: Estimate Tax - computing PIT")

    net_amount = state["income_data"]["grand_total"]["net_amount"]
    state["tax_estimate"] = estimate_pit(net_amount)
    state["status"] = "completed"
    state["messages"].append({
        "role": "system",
        "content": f"Tax estimate: {state['tax_estimate']['tax_due']} THB due",
    })

    return state


# ---------------------------------------------------------------------------
# Tax Q&A node (no receipt, free-text question only)
# ---------------------------------------------------------------------------

def tax_question_node(state: AgentState) -> AgentState:
    """Answer a free-text tax question using RAG."""
    logger.info("Node: Tax Q&A - answering question")

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
    START -> Router (income sync? has image? else question)
          -> Income -> Estimate Tax -> END
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
    workflow.add_node("income", income_node)
    workflow.add_node("estimate_tax", estimate_tax_node)

    # Entry point: decide income sync vs receipt vs question
    workflow.set_conditional_entry_point(
        should_inspect_receipt,
        {
            "income": "income",
            "inspect": "inspect",
            "tax_question": "tax_question",
        }
    )

    # After Income, estimate PIT
    workflow.add_edge("income", "estimate_tax")
    workflow.add_edge("estimate_tax", END)

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
# Compiled graph singleton
# ---------------------------------------------------------------------------
# Compiled exactly once, at module import time (i.e. application startup),
# and reused for every request. Never call build_workflow() per request.
compiled_graph = build_workflow()
logger.info("LangGraph workflow compiled (nodes: inspect, tax_expert, accountant, human_input, tax_question, income, estimate_tax)")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_receipt_workflow(
    user_id: str,
    image_path: Optional[str] = None,
    image_bytes: Optional[bytes] = None,
    image_url: Optional[str] = None,
) -> AgentState:
    """Run a receipt upload through the compiled graph.

    Used by the /receipts endpoints so every upload flows through
    Inspector -> Validator -> Tax Expert -> Accountant.
    """
    initial_state = {
        "question": "",
        "image_path": image_path,
        "image_bytes": image_bytes,
        "image_url": image_url,
        "receipt_data": {},
        "tax_analysis": {},
        "tax_advice": "",
        "needs_human_input": False,
        "missing_fields": [],
        "status": "",
        "accountant_result": {},
        "user_id": user_id,
        "seller_id": None,
        "period": None,
        "income_data": {},
        "tax_estimate": {},
        "messages": [],
    }
    return compiled_graph.invoke(initial_state)


def run_tax_assistant(question: str, image_path: str = None, user_id: str = "demo-user-id"):
    """Run the tax assistant workflow (CLI/demo entry point)."""
    print("=" * 60)
    print("TicTaxFlow AI Assistant")
    print("=" * 60)

    initial_state = {
        "question": question,
        "image_path": image_path,
        "image_bytes": None,
        "image_url": None,
        "receipt_data": {},
        "tax_analysis": {},
        "tax_advice": "",
        "needs_human_input": False,
        "missing_fields": [],
        "status": "",
        "accountant_result": {},
        "user_id": user_id,
        "seller_id": None,
        "period": None,
        "income_data": {},
        "tax_estimate": {},
        "messages": [{"role": "user", "content": question}],
    }

    result = compiled_graph.invoke(initial_state)

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
