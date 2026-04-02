import os
import json
from openai import OpenAI
from env import DropshippingEnv
from tasks import grade_task_1, grade_task_2, grade_task_3

def main():
    # Environment Variables
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
- noop()"""

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    print("--- Starting Dropshipping Simulation ---\n")

    for step in range(1, MAX_STEPS + 1):
        print(f"--- Step {step} ---")
        state_str = env.state()
        
        # Append current state to history
        messages.append({"role": "user", "content": f"Current State:\n{state_str}\n\nWhat is your next action?"})

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=200,
                temperature=0.0
            )
            action_string = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"API call failed: {str(e)}")
            action_string = "noop()"

        print(f"Agent Action: {action_string}")

        # Append assistant's action to history
        messages.append({"role": "assistant", "content": action_string})

        new_state, reward, done, info = env.step(action_string)
        print(f"Environment Info: {info['message']} (Error: {info['error']})\n")

        if done:
            print("Environment returned done=True. Ending early.\n")
            break

    print("--- Simulation Complete ---\n")

    # Evaluation
    final_state_json = env.state()
    score_1 = grade_task_1(final_state_json)
    score_2 = grade_task_2(final_state_json)
    score_3 = grade_task_3(final_state_json)

    print("--- Final Evaluation Scores ---")
    print(f"Task 1 (Update Inventory out of stock): {score_1:.2f} / 1.00")
    print(f"Task 2 (Issue Refund & Reply Ticket): {score_2:.2f} / 1.00")
    print(f"Task 3 (Update Competitor Pricing margin): {score_3:.2f} / 1.00")

if __name__ == "__main__":
    main()
