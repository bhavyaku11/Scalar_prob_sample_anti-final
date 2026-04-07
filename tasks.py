import json

def grade_task_1(final_state_json: str, env) -> float:
    """Checks if the agent zeroed out the supplier-flagged out-of-stock product."""
    try:
        state = json.loads(final_state_json)
        target_product = env._out_of_stock_product
        if state["inventory"].get(target_product, {}).get("stock") == 0:
            return 0.99  # Validated: strictly between 0 and 1
    except Exception:
        pass
    return 0.01  # Validated: strictly between 0 and 1

def grade_task_2(final_state_json: str, env) -> float:
    """Checks if the agent issued a >=15% refund AND replied to the delayed ticket."""
    try:
        state = json.loads(final_state_json)
        target_ticket = env._ticket_id
        refunds = state.get("refunds_issued", [])
        replies = state.get("ticket_replies", [])

        refund_ok = any(
            r.get("ticket_id") == target_ticket and r.get("percentage", 0) >= 15
            for r in refunds
        )
        reply_ok = any(r.get("ticket_id") == target_ticket for r in replies)

        if refund_ok and reply_ok:
            return 0.99
        elif refund_ok or reply_ok:
            return 0.5
    except Exception:
        pass
    return 0.01

def grade_task_3(final_state_json: str, env) -> float:
    """Checks if the agent re-priced the competitor product within margin rules.
    
    Rules:
      - Must be at least 5% cheaper than the competitor price.
      - Must maintain at least 20% profit margin: (Retail - Cost) / Retail >= 0.20
    """
    try:
        state = json.loads(final_state_json)
        target_product = env._competitor_product
        competitor_price = env._competitor_price

        prod = state["inventory"].get(target_product, {})
        new_price = prod.get("retail_price", 999)
        cost = prod.get("cost_price", 0)

        target_max = round(competitor_price * 0.95, 2)
        min_margin_price = round(cost / 0.80, 2)

        if min_margin_price <= new_price <= target_max:
            return 0.99
    except Exception:
        pass
    return 0.01
