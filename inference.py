import os
import json
from openai import OpenAI
from env import DropshippingEnv

# --- GRADER FUNCTIONS (Moved here so the robot can't miss them) ---
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
        if refund_ok or reply_ok: return 0.5
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

# --- MAIN INFERENCE LOGIC ---
def main():
    api_base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.environ.get("MODEL_NAME", "gpt-4o-mini")
    hf_token = os.environ.get("HF_TOKEN", "sk-mock-key")

    client = OpenAI(base_url=api_base_url, api_key=hf_token)
    env = DropshippingEnv()
    MAX_STEPS = 5

    system_prompt = """You are an autonomous Dropshipping Operations Manager. Manage the store by taking ONE action:
- update_inventory(product_id: str, new_stock_level: int)
- issue_refund(ticket_id: str, refund_percentage: int)
- update_price(product_id: str, new_retail_price: float)
- reply_ticket(ticket_id: str, message: str)
- noop()"""

    messages = [{"role": "system", "content": system_prompt}]
    print("[START] task=dropshipping", flush=True)
    
    final_step_count = 0
    for step in range(1, MAX_STEPS + 1):
        final_step_count = step
        state_str = env.state()
        messages.append({"role": "user", "content": f"State:\n{state_str}"})
        try:
            response = client.chat.completions.create(model=model_name, messages=messages, temperature=0.0)
            action_string = response.choices[0].message.content.strip()
        except: action_string = "noop()"

        messages.append({"role": "assistant", "content": action_string})
        new_state, reward, done, info = env.step(action_string)
        print(f"[STEP] step={step} reward={reward}", flush=True)
        if done: break

    # Final Evaluation
    final_state_json = env.state()
    s1, s2, s3 = grade_task_1(final_state_json, env), grade_task_2(final_state_json, env), grade_task_3(final_state_json, env)
    total = (s1 + s2 + s3) / 3.0
    
    print(f"[END] task=dropshipping score={total:.2f} steps={final_step_count} task1={s1:.2f} task2={s2:.2f} task3={s3:.2f}", flush=True)

if __name__ == "__main__":
    main()
