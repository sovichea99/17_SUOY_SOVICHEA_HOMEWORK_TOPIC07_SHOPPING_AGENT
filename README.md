# Shopping Agent

A small agentic application for **Topic 07 — Autonomous Agents & Tool Integration**.

The project demonstrates a simple shopping agent that can receive a user request, decide which tool to use, execute the tool, observe the result, and continue until it can return a final answer.

The project focuses on the **required/basic homework requirements**:
- Simple agent loop
- 4 tools
- Tool implementations and input schemas
- Application-level permission control
- Basic input validation
- Basic error handling
- Maximum tool-call limit

Product data is stored in a simple in-memory Python list. No database is required.

---

## 1. Project Overview

The **Simple Safe Shopping Agent** is a shopping assistant powered by a local LLM through **Ollama**.

A user can log in as either:

- `customer`
- `admin`

The user then sends a shopping request. The LLM decides whether it needs a tool and returns a structured JSON action.

The application receives that action and passes it through the safety harness before executing the tool.

The basic flow is:

```text
User Request
      ↓
Agent / LLM
      ↓
Tool Selection + Structured Arguments
      ↓
Permission Check
      ↓
Input Validation
      ↓
Tool Execution
      ↓
Tool Result
      ↓
Agent Observes Result
      ↓
Agent Decides Again
      ↓
Another Tool OR Final Answer
```

The agent is limited to a maximum of **5 tool calls per request**.

---

## 2. Available Tools

The product data is stored in the `PRODUCTS` list in `mockdata.py`.

| Tool | Purpose | Customer | Admin |
|---|---|:---:|:---:|
| `search_products(query)` | Search products by name or category | ✓ | ✓ |
| `check_stock(product_id)` | Check the current stock of a product | ✓ | ✓ |
| `buy_product(product_id, quantity)` | Buy a product when enough stock is available | ✓ | ✓ |
| `delete_product(product_id)` | Delete a product from the store | ✗ | ✓ |

### Tool implementation

The actual business logic is implemented in:

```text
tools.py
```

### Tool schemas

Each tool has a Pydantic input schema in:

```text
schemas.py
```

The schemas define the expected input types and basic constraints.

Examples:

```python
product_id: int = Field(gt=0)
```

```python
quantity: int = Field(gt=0)
```

This means product IDs and purchase quantities must be greater than zero.

---

## 3. Agent Loop

The main agent loop is implemented in:

```text
agent.py
```

The application follows this process:

1. Receive a user request.
2. Send the request to the local LLM.
3. The LLM decides whether a tool is needed.
4. The LLM selects a tool and provides structured arguments in JSON.
5. `harness.py` checks whether the tool is allowed for the current role.
6. The tool arguments are validated using the corresponding Pydantic schema.
7. The tool is executed.
8. The tool result is returned to the agent as an observation.
9. The LLM decides what to do next.
10. The agent either calls another tool or returns a final answer.
11. The process stops when a final answer is produced or the maximum tool-call limit is reached.

### Example flow

```text
User:
"Find a laptop that is currently in stock."

        ↓

Agent / LLM:
search_products("laptop")

        ↓

Tool Result:
MacBook Air M1
Dell Inspiron 15

        ↓

Agent / LLM observes the result

        ↓

Agent / LLM:
check_stock(product_id=1)

        ↓

Tool Result:
MacBook Air M1 has 5 units in stock.

        ↓

Agent / LLM:
Final answer

        ↓

"The MacBook Air M1 is in stock (5 units, $700)."
```

The important part is that the result of the first tool call is used by the agent to decide whether another tool call is needed.

---

## 4. Permission Rule

Permission is enforced in **application code inside `harness.py`**.

It is not only described in the LLM prompt.

The permission rules are:

| Action | Customer | Admin |
|---|:---:|:---:|
| `search_products` | ✓ | ✓ |
| `check_stock` | ✓ | ✓ |
| `buy_product` | ✓ | ✓ |
| `delete_product` | ✗ | ✓ |

For example, if a customer requests:

```text
delete product 1
```

the application checks the customer's permissions before executing `delete_product`.

The result is:

```text
PERMISSION_DENIED
```

The `delete_product()` function is not executed, so the product is not removed.

This demonstrates application-level permission control.

---

## 5. Safety

The project includes the required basic safety controls.

### 5.1 Input Validation

Tool inputs are validated in `harness.py` using the Pydantic schemas from `schemas.py`.

Examples:

```text
product_id > 0
quantity > 0
query must contain at least 2 character
```

Invalid arguments are rejected before the actual tool function is executed.

Example:

```text
quantity = 0
```

returns a controlled validation error instead of executing the purchase.

---

### 5.2 Permission Check

Before executing a tool, `harness.py` checks whether the current role is allowed to use that tool.

For example:

```text
customer + delete_product
        ↓
PERMISSION_DENIED
        ↓
delete_product is not executed
```

---

### 5.3 Error Handling

Tool execution is wrapped in error handling.

If an unexpected error happens inside a tool, the application returns a controlled result such as:

```json
{
  "success": false,
  "error": "TOOL_EXECUTION_ERROR"
}
```

Other controlled errors include:

```text
UNKNOWN_TOOL
PERMISSION_DENIED
INVALID_ARGUMENTS
PRODUCT_NOT_FOUND
INSUFFICIENT_STOCK
```

The main application also has a final exception handler so that an unexpected application error does not crash the whole interaction.

---

### 5.4 Maximum Tool-Call Limit

The agent has:

```python
MAX_TOOL_CALLS = 5
```

The loop stops after the maximum number of tool calls is reached.

This prevents an endless agent loop.

---

## 6. Example Run

### Example 1 — Agent uses multiple tools

Available roles:
1. customer
2. admin

Enter your role: customer

Logged in as: customer
Type 'exit' to quit.

You: Find a laptop that is currently in stock

--- Agent Decision ---
{
  "tool": "search_products",
  "arguments": {
    "query": "in stock laptop",
    "all": true
  }
}

--- Tool Call ---
Tool: search_products
Arguments: {'query': 'in stock laptop', 'all': True}

--- Tool Result ---
{'success': True, 'products': [{'id': 1, 'name': 'MacBook Air M1', 'category': 'laptop', 'price': 700, 'stock': 5}]}

--- Agent Decision ---
{
  "tool": "check_stock",
  "arguments": {
    "product_id": 1
  }
}

--- Tool Call ---
Tool: check_stock
Arguments: {'product_id': 1}

--- Tool Result ---
{'success': True, 'product_id': 1, 'product_name': 'MacBook Air M1', 'stock': 5}

Agent:
Product MacBook Air M1 has 5 units in stock.

```

This example demonstrates:

```text
User Request
→ search_products
→ observe result
→ check_stock
→ observe result
→ final answer
```
---

## 7. Project Structure

```text
my-shopping-agents/
├── README.md
├── main.py
├── agent.py
├── tools.py
├── schemas.py
├── harness.py
├── system_prompt.py
├── mockdata.py
└── requirement.txt
```

### File responsibilities

| File | Responsibility |
|---|---|
| `main.py` | Starts the application, accepts the role and user requests |
| `agent.py` | Calls the LLM, runs the agent loop, parses tool actions |
| `tools.py` | Contains the actual shopping tool implementations |
| `schemas.py` | Defines Pydantic input schemas |
| `harness.py` | Handles permissions, validation, safe tool execution, and tool-call limit |
| `system_prompt.py` | Defines the instructions given to the LLM |
| `mockdata.py` | Contains the in-memory product data |
| `README.md` | Project documentation and run instructions |

---

## 8. Requirements

The project uses:

- Python
- Ollama
- `llama3.2:3b`
- Pydantic

Python dependencies are listed in:

```text
requirement.txt
```

---

## 9. Run Instructions

### Step 1 — Install Ollama

Install Ollama and make sure it is running.

Pull the model used by the project:

```bash
ollama pull llama3.2:3b
```

### Step 2 — Install Python dependencies

From the project directory:

```bash
pip install -r requirement.txt
```

### Step 3 — Run the agent

```bash
python main.py
```

### Step 4 — Choose a role

The application supports:

```text
customer
admin
```

### Step 5 — Enter a request

Examples:

```text
Find a laptop that is currently in stock
```

```text
Check stock for product 1
```

```text
Buy 2 of product 1
```

```text
Delete product 2
```

`delete_product` is available only to the `admin` role.

Type:

```text
exit
```

to stop the application.

---
