import json
import sys
import os

sys.path.insert(0, '/app')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

__all__ = ['grade_task_1', 'grade_task_2', 'grade_task_3']

def grade_task_1(final_state_json: str, env) -> float:
    try:
        state = json.loads(final_state_json)
        target_product = env._out_of_stock_product
        stock = state["inventory"].get(target_product, {}).get("stock", -1)
        if stock == 0:
            return 0.99
    except Exception:
        pass
    return 0.01

def grade_task_2(final_state_json: str, env) -> float:
    try:
        state = json.loads(final_state_json)
        target_ticket = env._ticket_id
        refund_ok = any(
            r.get("ticket_id") == target_ticket and r.get("percentage", 0) >= 15
            for r in state.get("refunds_issued", [])
        )
        reply_ok = any(
            r.get("ticket_id") == target_ticket
            for r in state.get("ticket_replies", [])
        )
        if refund_ok and reply_ok:
            return 0.99
    except Exception:
        pass
    return 0.01

def grade_task_3(final_state_json: str, env) -> float:
    try:
        state = json.loads(final_state_json)
        prod = state["inventory"].get(env._competitor_product, {})
        new_price = prod.get("retail_price", 999)
        cost = prod.get("cost_price", 0)
        target_max = round(env._competitor_price * 0.95, 2)
        min_margin_price = round(cost / 0.80, 2)
        if min_margin_price <= new_price <= target_max:
            return 0.99
    except Exception:
        pass
    return 0.01
