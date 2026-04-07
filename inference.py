import os
import json
from openai import OpenAI
from env import DropshippingEnv
from tasks import grade_task_1, grade_task_2, grade_task_3


def main():
    api_base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.environ.get("MODEL_NAME", "gpt-4o-mini")
    hf_token = os.environ.get("HF_TOKEN", "sk-mock-key")

    client = OpenAI(
        base_url=api_base_url,
        api_key=hf_token
    )

    env = DropshippingEnv()
    MAX_STEPS = 5

    system_prompt = """You are an autonomous Dropshipping Operations Manager. Your job is to manage a simulated e-commerce storefront by reading the current business state and taking exactly ONE action per turn.

You must reply with exactly one of the following function calls. Do not include any conversational text:
- update_inventory(product_id: str, new_stock_level: int)
- issue_refund(ticket_id: str, refund_percentage: int)
- update_price(product_id: str, new_retail_price: float)
- reply_ticket(ticket_id: str, message: str)
- noop()

Rules:
- If a supplier says a product is out of stock, update the inventory to 0.
- If adjusting prices against competitors, you must maintain at least a 20% profit margin ((Retail - Cost) / Retail >= 0.20) while staying at least 5% cheaper than the competitor price.
- If a customer complains about a delayed package (over 7 days late), issue a 15% partial refund and reply to the ticket with an apology."""

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    print("=" * 60)
    print("  DROPSHIPPING OPERATIONS SIMULATION")
    print("=" * 60)

    print("[START] task=dropshipping", flush=True)
    
    for step in range(1, MAX_STEPS + 1):
        print(f"\n--- Step {step}/{MAX_STEPS} ---")
        state_str = env.state()

        messages.append({
            "role": "user",
            "content": f"Current State:\n{state_str}\n\nWhat is your next action?"
        })

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=200,
                temperature=0.0
            )
            action_string = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  API call failed: {str(e)}")
            action_string = "noop()"

        print(f"  Agent Action: {action_string}")

        messages.append({"role": "assistant", "content": action_string})

        print(f"[STEP] step={step} reward={reward}", flush=True)
        
        new_state, reward, done, info = env.step(action_string)
        print(f"  Reward: {reward:+.2f} | Done: {done}")
        print(f"  Info: {info['message']} (Error: {info['error']})")

        if done:
            print("\n  All tasks solved! Ending episode early.")
            break

    # --- Final Evaluation ---
    print("\n" + "=" * 60)
    print("  FINAL EVALUATION SCORES")
    print("=" * 60)

    final_state_json = env.state()
    score_1 = grade_task_1(final_state_json, env)
    score_2 = grade_task_2(final_state_json, env)
    score_3 = grade_task_3(final_state_json, env)

    print(f"  Task 1 (Supplier Stock-Out):      {score_1:.2f} / 1.00")
    print(f"  Task 2 (Refund & Reply Ticket):    {score_2:.2f} / 1.00")
    print(f"  Task 3 (Competitive Re-Pricing):   {score_3:.2f} / 1.00")
    print(f"  ---")
    print(f"  Total:                             {score_1 + score_2 + score_3:.2f} / 3.00")
    print("=" * 60)

final_total_score = (score_1 + score_2 + score_3) / 3.0
print(f"[END] task=dropshipping score={final_total_score:.2f} steps={MAX_STEPS}", flush=True)

if __name__ == "__main__":
    main()
