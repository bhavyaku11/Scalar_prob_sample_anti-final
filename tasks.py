import json

def grade_task_1(final_state_json: str) -> float:
    try:
        state = json.loads(final_state_json)
        if state["inventory"].get("PROD_001", {}).get("stock") == 0:
            return 1.0
    except:
        pass
    return 0.0

def grade_task_2(final_state_json: str) -> float:
    try:
        state = json.loads(final_state_json)
        refunds = state.get("refunds_issued", [])
        replies = state.get("ticket_replies", [])
        
        refund_issued = any(r.get("ticket_id") == "TICK_882" and r.get("percentage", 0) >= 15 for r in refunds)
        reply_sent = any(r.get("ticket_id") == "TICK_882" for r in replies)
        
        if refund_issued and reply_sent:
            return 1.0
        elif refund_issued or reply_sent:
            return 0.5
    except:
        pass
    return 0.0

def grade_task_3(final_state_json: str) -> float:
    try:
        state = json.loads(final_state_json)
        price = state["inventory"].get("PROD_003", {}).get("retail_price", 34.99)
        if 15.0 <= price <= 26.60:
            return 1.0
    except:
        pass
    return 0.0
