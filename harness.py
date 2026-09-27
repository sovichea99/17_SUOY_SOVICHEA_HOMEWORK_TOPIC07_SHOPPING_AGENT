from schemas import (
    SearchProductInput,
    CheckStockInput,
    BuyProductInput,
    DeleteProductInput,
)

MAX_TOOL_CALLS = 5

PERMISSIONS = {
    "customer": {"search_products", "check_stock", "buy_product"},
    "admin": {"search_products", "check_stock", "buy_product", "delete_product"},
}

SCHEMAS = {
    "search_products": SearchProductInput,
    "check_stock": CheckStockInput,
    "buy_product": BuyProductInput,
    "delete_product": DeleteProductInput,
}


def execute_tool(role: str, tool_name: str, arguments: dict, tools: dict) -> dict:
    """
    Safely run one tool call:
      1. tool must exist (allowlist against the registered tools dict)
      2. role must be permitted to use it
      3. arguments must pass the tool's schema
      4. run it, catching any unexpected error
    Always returns a plain dict, never raises.
    """

    if tool_name not in tools:
        return {
            "success": False,
            "error": "UNKNOWN_TOOL",
            "message": f"Tool '{tool_name}' does not exist.",
        }

    allowed_tools = PERMISSIONS.get(role, set())
    if tool_name not in allowed_tools:
        return {
            "success": False,
            "error": "PERMISSION_DENIED",
            "message": f"Role '{role}' is not allowed to use '{tool_name}'.",
        }

    schema = SCHEMAS[tool_name]
    try:
        validated_args = schema(**arguments)
    except Exception as error:
        validation_messages = []
        for validation_error in error.errors():
            field_name = validation_error["loc"][0]
            field = schema.model_fields.get(field_name)
            if validation_error["type"] == "missing":
                message = f"'{field_name}' is required."
            elif field and field.description:
                message = field.description
            else:
                message = validation_error["msg"
                                           ]
            validation_messages.append(message)
        return {
            "success": False,
            "error": "INVALID_ARGUMENTS",
            "message": f"Invalid arguments for '{tool_name}': "
            + "; ".join(validation_messages),
        }

    try:
        return tools[tool_name](**validated_args.model_dump())
    except Exception as error:
        return {
            "success": False,
            "error": "TOOL_EXECUTION_ERROR",
            "message": f"Tool '{tool_name}' failed: {error}",
        }
