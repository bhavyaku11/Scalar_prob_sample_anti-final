import os
import json
from openai import OpenAI
from env import DropshippingEnv

# --- GRADER FUNCTIONS (Required for Task Validation) ---
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
        refunds = state.get("refunds_issued", [])
        replies = state.get("ticket_replies", [])
        refund_ok = any(r.get("ticket_id") == target_ticket and r.get("percentage", 0) >= 15 for r in refunds)
        reply_ok = any(r.get("ticket_id") == target_ticket for r in replies)
        if refund_ok and reply_ok: return 0.99
    except: pass
    return 0.01

def grade_task_3(final_state_json: str, env) -> float:
    try:
        state = json.loads(final_state_json)
        prod = state["inventory"].get(env._competitor_product, {})
        new_price = prod.get("retail_price", 999)
        cost = prod.get("cost_price", 0)
        target_max = round(env._competitor_price * 0.95, 2)
        min_margin_price = round(cost / 0.80, 2)
        if min_margin_price <= new_price <= target_max: return 0.99
    except: pass
    return 0.01

def main():
    # --- CHECKLIST FIX: No default for HF_TOKEN ---
    api_base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
    hf_token = os.getenv("HF_TOKEN") # Strictly no default value here

    # Configure OpenAI client using these variables
    client = OpenAI(
        base_url=api_base_url,
        api_key=hf_token
    )

    env = DropshippingEnv()
    MAX_STEPS = 5

    # --- CHECKLIST FIX: Structured Logs (START) ---
    print("[START] task=dropshipping", flush=True)
    
    messages = [{"role": "system", "content": "You are a Dropshipping Manager. Reply only with function calls."}]
    
    for step in range(1, MAX_STEPS + 1):
        state_str = env.state()
        messages.append({"role": "user", "content": state_str})
        
        try:
            response = client.chat.completions.create(
                model=model_name, 
                messages=messages, 
                temperature=0.0
            )
            action = response.choices[0].message.content.strip()
        except: 
            action = "noop()"
        
        messages.append({"role": "assistant", "content": action})
        new_state, reward, done, info = env.step(action)
        
        # --- CHECKLIST FIX: Structured Logs (STEP) ---
        print(f"[STEP] step={step} reward={reward}", flush=True)
        
        if done:
            break

    # Final Evaluation
    final_state = env.state()
    s1 = grade_task_1(final_state, env)
    s2 = grade_task_2(final_state, env)
    s3 = grade_task_3(final_state, env)
    avg = (s1 + s2 + s3) / 3.0
    
    # --- CHECKLIST FIX: Structured Logs (END) ---
    print(f"[END] task=dropshipping score={avg:.2f} steps={MAX_STEPS} task1={s1:.2f} task2={s2:.2f} task3={s3:.2f}", flush=True)

if __name__ == "__main__":
    main()
