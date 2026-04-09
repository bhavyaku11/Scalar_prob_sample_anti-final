import json

# This list helps the grader discover the functions
__all__ = ['grade_task_1', 'grade_task_2', 'grade_task_3']

def grade_task_1(final_state_json: str, env) -> float:
    try:
        state = json.loads(final_state_json)
        target_product = env._out_of_stock_product
        if state["inventory"].get(target_product, {}).get("stock") == 0:
            return 0.99
    except: pass
    return 0.01

def grade_task_2(final_state_json: str, env) -> float:
    try:
        state = json.loads(final_state_json)
        target_ticket = env._ticket_id
        refund_ok = any(r.get("ticket_id") == target_ticket and r.get("percentage", 0) >= 15 for r in state.get("refunds_issued", []))
        reply_ok = any(r.get("ticket_id") == target_ticket for r in state.get("ticket_replies", []))
        if refund_ok and reply_ok: return 0.99
    except: pass
    return 0.01

def grade_task_3(final_state_json: str, env) -> float:
    try:
        state = json.loads(final_state_json)
        prod = state["inventory"].get(env._competitor_product, {})
        new_price = prod.get("retail_price", 999)
        if round(prod.get("cost_price", 0) / 0.80, 2) <= new_price <= round(env._competitor_price * 0.95, 2):
            return 0.99
    except: pass
    return 0.01
