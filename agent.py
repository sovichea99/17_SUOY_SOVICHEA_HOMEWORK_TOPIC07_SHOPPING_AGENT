import json
import ollama

from tools import (
    search_products,
    check_stock,
    buy_product,
    delete_product,
)
from system_prompt import SYSTEM_PROMPT
from harness import (
    execute_tool,
    MAX_TOOL_CALLS,
)

MODEL = "llama3.2:3b"

TOOL_FUNCTIONS = {
    "search_products": search_products,
    "check_stock": check_stock,
    "buy_product": buy_product,
    "delete_product": delete_product,
}

PURCHASE_WORDS = {"buy", "purchase", "order", "checkout"}

def ask_llama(messages: list) -> str:

    response = ollama.chat(
        model=MODEL,
        messages=messages,
    )

    return response["message"]["content"]


def run_agent(
    user_request: str,
    role: str = "customer"
) -> dict:

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_request,
        },
    ]

    tool_call_count = 0

    while tool_call_count < MAX_TOOL_CALLS:

        response = ask_llama(messages)

        print("\n--- Agent Decision ---")
        print(response)

        try:
            action = json.loads(response)

        except json.JSONDecodeError:
            return {"answer": response}

        #check expected structure
        tool_name = action.get("tool")
        arguments = action.get("arguments", {})

        if tool_name == "final":

            return {
                "answer": action.get(
                    "answer",
                    "I have completed the request."
                )
            }
        #unknown action
        if not tool_name:

            return {
                "answer": "I could not determine the next safe action."
            }
        if (
            tool_name == "buy_product"
            and not any(
                word in user_request.lower().split()
                for word in PURCHASE_WORDS
            )
        ):
            return {
                "answer": (
                    "Please explicitly ask to buy, purchase, or order "
                    "a product."
                )
            }
        #count tool call
        tool_call_count += 1
        print("\n--- Tool Call ---")
        print(f"Tool: {tool_name}")
        print(f"Arguments: {arguments}")

        result = execute_tool(
            role=role,
            tool_name=tool_name,
            arguments=arguments,
            tools=TOOL_FUNCTIONS,
        )

        print("\n--- Tool Result ---")
        print(result)

        if result.get("error") in {
            "INVALID_ARGUMENTS",
            "PERMISSION_DENIED",
            "INSUFFICIENT_STOCK",
        }:
            return {"answer": result["message"]}
        
        if result.get("success") is True:
            if tool_name == "delete_product":
                return {
                    "answer": result.get(
                    "message",
                    "The product was deleted successfully."
                    )
                }

            if tool_name == "buy_product":
                return {
                    "answer": result.get(
                    "message",
                    "The product was purchased successfully."
                    )
                }

            if tool_name == "check_stock":
                return {
                    "answer": (
                        f"Product {result.get('product_name', '')} "
                        f"has {result.get('stock', 0)} units in stock."
                    )
                }
                
        messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )
        messages.append(
            {
                "role": "user",
                "content": (
                    "Tool result:\n"
                    + json.dumps(result)
                    + "\n\n"
                    "Now decide what to do next. "
                    "If more information is needed, "
                    "choose another tool. "
                    "Otherwise return the final answer."
                ),
            }
        )
    return {
        "answer": (
            "I stopped because the maximum number "
            "of tool calls was reached."
        )
    }