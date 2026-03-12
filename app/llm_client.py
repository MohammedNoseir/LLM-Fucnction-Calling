import json
from app.schemas import CurrencyConversion, InvoiceSchema
from app.tools import convert_currency, generate_invoice
from app.security import sanitize_string

def mock_llm(prompt: str) -> dict:
    """Simulates an LLM parsing natural language into structured tool calls."""
    prompt_lower = prompt.lower()
    
    if "convert" in prompt_lower:
        return {
            "tool_calls": [{
                "name": "convert_currency",
                "arguments": {"amount": 100.0, "from_currency": "USD", "to_currency": "EGP"}
            }]
        }
    elif "invoice" in prompt_lower:
        return {
            "tool_calls": [{
                "name": "generate_invoice",
                "arguments": {
                    "customer_name": "Alice",
                    "items": [{"name": "Laptop", "price": 1200.0}, {"name": "Mouse", "price": 25.0}]
                }
            }]
        }
    return {"tool_calls": []}

def run_llm(prompt: str) -> str:
    llm_response = mock_llm(prompt)
    tool_calls = llm_response.get("tool_calls", [])

    for call in tool_calls:
        name = call["name"]
        args = call["arguments"]

        if name == "convert_currency":
            # Validation
            validated_data = CurrencyConversion(**args)
            return convert_currency(
                validated_data.amount, 
                validated_data.from_currency, 
                validated_data.to_currency
            )

        elif name == "generate_invoice":
            # Sanitization & Validation
            args["customer_name"] = sanitize_string(args["customer_name"])
            validated_data = InvoiceSchema(**args)
            # Convert Pydantic objects back to dicts for the tool
            items_list = [item.model_dump() for item in validated_data.items]
            return generate_invoice(validated_data.customer_name, items_list)

    return "Tool execution failed."