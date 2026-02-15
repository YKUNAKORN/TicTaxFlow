import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from inspector_agent import extract_receipt_json
from tax_expert_agent import ask_tax_expert

load_dotenv()


class AgentState(TypedDict):
    """State for the tax assistant workflow."""
    question: str
    image_path: str
    receipt_data: dict
    tax_advice: str
    needs_human_input: bool
    messages: Annotated[list, add_messages]


def should_inspect_receipt(state: AgentState) -> str:
    """Decide if we need to inspect a receipt image."""
    if state.get("image_path"):
        return "inspect"
    return "tax_expert"


def inspect_receipt_node(state: AgentState) -> AgentState:
    """Extract data from receipt image."""
    print("Node 1: Inspector Agent - Analyzing receipt...")
    
    image_path = state["image_path"]
    receipt_data = extract_receipt_json(image_path)
    
    state["receipt_data"] = receipt_data
    state["messages"].append({
        "role": "system",
        "content": f"Receipt extracted: {receipt_data}"
    })
    
    print(f"Extracted: date={receipt_data.get('date')}, amount={receipt_data.get('amount')}, tax_id={receipt_data.get('tax_id')}")
    
    return state


def validate_receipt_data(state: AgentState) -> str:
    """Check if receipt data is complete."""
    receipt_data = state.get("receipt_data", {})
    
    # Check if all required fields exist and are not null or error
    date = receipt_data.get("date")
    amount = receipt_data.get("amount")
    tax_id = receipt_data.get("tax_id")
    
    has_error = receipt_data.get("error")
    
    if has_error:
        print("Validation: Receipt has extraction error → Human input needed")
        return "human_input"
    
    if date and amount and tax_id:
        print("Validation: Data complete → Proceed to Tax Expert")
        return "tax_expert"
    else:
        missing_fields = []
        if not date:
            missing_fields.append("date")
        if not amount:
            missing_fields.append("amount")
        if not tax_id:
            missing_fields.append("tax_id")
        
        print(f"Validation: Missing fields: {', '.join(missing_fields)} → Human input needed")
        return "human_input"


def human_input_node(state: AgentState) -> AgentState:
    """Handle incomplete data - ask user for missing information."""
    print("\nHuman-in-the-loop: Incomplete receipt data detected")
    
    receipt_data = state.get("receipt_data", {})
    missing_fields = []
    
    if not receipt_data.get("date"):
        missing_fields.append("date")
    if not receipt_data.get("amount"):
        missing_fields.append("amount")
    if not receipt_data.get("tax_id"):
        missing_fields.append("tax_id")
    
    message = f"Cannot read receipt clearly. Please provide: {', '.join(missing_fields)}"
    
    state["needs_human_input"] = True
    state["messages"].append({
        "role": "system",
        "content": message
    })
    
    print(f"Requesting from user: {', '.join(missing_fields)}")
    print("Note: In production, this would pause and wait for user input")
    
    return state


def tax_expert_node(state: AgentState) -> AgentState:
    """Get tax advice from expert agent."""
    print("Node 2: Tax Expert Agent - Analyzing question...")
    
    question = state["question"]
    
    # Use receipt data if available from Inspector
    if state.get("receipt_data") and state["receipt_data"]:
        receipt_data = state["receipt_data"]
        enhanced_question = f"{question}\n\nReceipt details: Date: {receipt_data.get('date')}, Amount: {receipt_data.get('amount')}, Tax ID: {receipt_data.get('tax_id')}"
        question = enhanced_question
        print(f"Using receipt data from Inspector Agent")
    
    answer = ask_tax_expert(question)
    
    state["tax_advice"] = answer
    state["messages"].append({
        "role": "assistant",
        "content": answer
    })
    
    return state


def build_workflow():
    """Build the LangGraph workflow.
    
    Flow:
    START → Router (has image?)
         → Inspector → Validator (data complete?)
                    → Tax Expert (if complete) → END
                    → Human Input (if incomplete) → END
         → Tax Expert (if no image) → END
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("inspect", inspect_receipt_node)
    workflow.add_node("human_input", human_input_node)
    workflow.add_node("tax_expert", tax_expert_node)
    
    # Set conditional entry point (router)
    workflow.set_conditional_entry_point(
        should_inspect_receipt,
        {
            "inspect": "inspect",
            "tax_expert": "tax_expert"
        }
    )
    
    # Add conditional edge from Inspector based on data completeness
    workflow.add_conditional_edges(
        "inspect",
        validate_receipt_data,
        {
            "tax_expert": "tax_expert",
            "human_input": "human_input"
        }
    )
    
    # Connect Tax Expert → END
    workflow.add_edge("tax_expert", END)
    
    # Connect Human Input → END (wait for user action)
    workflow.add_edge("human_input", END)
    
    return workflow.compile()


def run_tax_assistant(question: str, image_path: str = None):
    """Run the tax assistant workflow."""
    print("=" * 60)
    print("TicTaxFlow AI Assistant")
    print("=" * 60)
    
    # Initialize state
    initial_state = {
        "question": question,
        "image_path": image_path,
        "receipt_data": {},
        "tax_advice": "",
        "needs_human_input": False,
        "messages": [{"role": "user", "content": question}]
    }
    
    # Build and run workflow
    app = build_workflow()
    result = app.invoke(initial_state)
    
    print("\n" + "=" * 60)
    print("Result:")
    print("=" * 60)
    
    if result.get("receipt_data"):
        print(f"\nReceipt Data:")
        for key, value in result["receipt_data"].items():
            print(f"  {key}: {value}")
    
    if result.get("needs_human_input"):
        print(f"\nStatus: Waiting for user input")
        print(f"Action required: Please provide missing information")
    elif result.get("tax_advice"):
        print(f"\nTax Advice:\n{result['tax_advice']}")
    
    print("=" * 60)
    
    return result


def main():
    """Test the workflow."""
    print("LangGraph Workflow - Tax Assistant")
    print("\nExample 1: Question only")
    print("-" * 60)
    
    result1 = run_tax_assistant("ประกันสังคมลดหย่อนได้เท่าไหร่?")
    
    print("\n\nExample 2: Question with receipt (if available)")
    print("-" * 60)
    
    test_image = "../data/receipts/sample_receipt.jpg"
    if os.path.exists(test_image):
        result2 = run_tax_assistant(
            "Can I use this receipt for tax deduction?",
            image_path=test_image
        )
    else:
        print("No test receipt found. Place an image at:")
        print(f"  {test_image}")
    
    print("\nWorkflow ready!")


if __name__ == "__main__":
    main()
