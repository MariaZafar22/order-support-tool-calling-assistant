"""
Function Calling: AI Assistant with a Custom Tool (Gemini)

Install first:
    pip install google-genai
(Google Colab: run  !pip install google-genai  in a cell first)

Get a FREE Gemini API key: https://aistudio.google.com/apikey

Flow:
 user request -> LLM decides if a tool is needed -> LLM returns tool name + arguments
 -> OUR application executes the function -> result is sent back to the LLM
 -> LLM writes the final answer
"""

import os
from getpass import getpass

from google import genai
from google.genai import types

# ---------------------------------------------------------------
# 0. Setup
# ---------------------------------------------------------------
API_KEY = os.environ.get("GEMINI_API_KEY") or getpass("Enter your Gemini API key: ")
MODEL_NAME = "gemini-2.5-flash"  # if this name gives an error, use another Gemini Flash model from AI Studio
client = genai.Client(api_key=API_KEY)

# ---------------------------------------------------------------
# 1. Fictional data + our local function (the "tool")
# ---------------------------------------------------------------
ORDERS = {
    "ORD-101": {"item": "Wireless Headphones", "status": "Shipped", "expected_delivery": "18 November 2026"},
    "ORD-102": {"item": "Laptop Stand", "status": "Processing", "expected_delivery": "22 November 2026"},
    "ORD-103": {"item": "USB-C Cable", "status": "Delivered", "expected_delivery": "10 November 2026"},
}


def check_order_status(order_id: str) -> dict:
    """Look up an order in our fictional database."""
    order = ORDERS.get(order_id.strip().upper())
    if order is None:
        return {"found": False, "message": f"No order exists with ID {order_id}."}
    return {"found": True, "order_id": order_id.strip().upper(), **order}


# Safety: the application decides which tools exist. The LLM can only
# ask for these names; it can never run arbitrary code.
AVAILABLE_TOOLS = {"check_order_status": check_order_status}

# ---------------------------------------------------------------
# 2. Tell the LLM about the tool (tool definition)
# ---------------------------------------------------------------
tool_definition = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="check_order_status",
            description="Get the current status and expected delivery date of a customer order using its order ID.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "order_id": types.Schema(
                        type="STRING",
                        description="The order ID, for example ORD-101",
                    )
                },
                required=["order_id"],
            ),
        )
    ]
)

config = types.GenerateContentConfig(
    tools=[tool_definition],
    # We run the tool ourselves, so turn off automatic execution
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    system_instruction=(
        "You are a customer support assistant for an online store. "
        "Use the check_order_status tool whenever the user asks about an order. "
        "Only report information returned by the tool. "
        "If the tool says an order was not found, tell the user clearly and ask them to check the ID. "
        "Never invent order details."
    ),
)


# ---------------------------------------------------------------
# 3. The tool-calling loop
# ---------------------------------------------------------------
def chat(user_message: str):
    print("=" * 70)
    print(f"USER: {user_message}")
    print("=" * 70)

    contents = [types.Content(role="user", parts=[types.Part(text=user_message)])]

    # Step A: send the request to the LLM
    response = client.models.generate_content(model=MODEL_NAME, contents=contents, config=config)

    # Step B: did the LLM ask for a tool?
    calls = response.function_calls
    if not calls:
        print("[1] AI TOOL REQUEST : none (answered without a tool)")
        print(f"[FINAL RESPONSE]    : {response.text}\n")
        return

    # Keep the model's tool request in the conversation
    contents.append(response.candidates[0].content)

    for call in calls:
        print(f"[1] AI TOOL REQUEST : {call.name}({dict(call.args)})")

        # Step C: OUR application executes the function (only if allowed)
        func = AVAILABLE_TOOLS.get(call.name)
        if func is None:
            result = {"error": f"Tool {call.name} is not available."}
        else:
            result = func(**call.args)
        print(f"[2] APP EXECUTED    : {call.name} -> {result}")

        # Step D: send the tool result back to the LLM
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_function_response(name=call.name, response={"result": result})],
            )
        )

    # Step E: LLM writes the final answer using the tool result
    final = client.models.generate_content(model=MODEL_NAME, contents=contents, config=config)
    print(f"[3] FINAL RESPONSE  : {final.text}\n")


# ---------------------------------------------------------------
# 4. Test cases
# ---------------------------------------------------------------
test_requests = [
    "Where is my order ORD-101?",                      # needs the tool
    "Has ORD-103 been delivered yet?",                 # needs the tool (different wording)
    "What is the capital of France?",                  # does NOT need the tool
    "Can you check the status of order ORD-999?",      # invalid order ID
]

for request in test_requests:
    chat(request)
