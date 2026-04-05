import json
import random

class DropshippingEnv:
    def __init__(self, seed=None):
        self.state_data = {}
        self._seed = seed
        self._tasks_solved = set()
        self.reset()

    def reset(self):
        """Initializes a randomized mock database for the dropshipping store."""
        if self._seed is not None:
            random.seed(self._seed)

        self._tasks_solved = set()

        # --- Product catalog (fixed structure, randomized pricing jitter) ---
        products = {
            "PROD_001": {"name": "Wireless Earbuds",    "cost_price": 15.00, "base_retail": 39.99, "stock": 150},
            "PROD_002": {"name": "Posture Corrector",   "cost_price": 4.50,  "base_retail": 19.99, "stock": 85},
            "PROD_003": {"name": "LED Desk Lamp",       "cost_price": 12.00, "base_retail": 34.99, "stock": 40},
            "PROD_004": {"name": "Phone Stand",         "cost_price": 3.00,  "base_retail": 14.99, "stock": 200},
            "PROD_005": {"name": "USB-C Hub",           "cost_price": 18.00, "base_retail": 49.99, "stock": 60},
        }

        inventory = {}
        product_ids = list(products.keys())
        for pid, info in products.items():
            jitter = round(random.uniform(-2.0, 2.0), 2)
            inventory[pid] = {
                "name": info["name"],
                "cost_price": info["cost_price"],
                "retail_price": round(info["base_retail"] + jitter, 2),
                "stock": info["stock"]
            }

        # --- Task 1: Randomly pick which product the supplier says is out of stock ---
        self._out_of_stock_product = random.choice(product_ids)
        oos_name = inventory[self._out_of_stock_product]["name"]

        supplier_inbox = [
            {
                "email_id": f"SUP_{random.randint(100, 999)}",
                "from": "Shenzhen Audio Factory",
                "subject": f"URGENT: {self._out_of_stock_product} Production Delay",
                "body": f"Due to component shortages, we are completely out of stock for the {oos_name} ({self._out_of_stock_product}). We cannot fulfill new orders for 3 weeks."
            }
        ]

        # --- Task 2: Customer complaint about a delayed package (>7 days) ---
        delayed_product_candidates = [p for p in product_ids if p != self._out_of_stock_product]
        self._delayed_product = random.choice(delayed_product_candidates)
        delayed_name = inventory[self._delayed_product]["name"]
        days_late = random.randint(8, 14)
        self._ticket_id = f"TICK_{random.randint(100, 999)}"
        self._order_id = f"ORD_{random.randint(1000, 9999)}"

        customer_tickets = [
            {
                "ticket_id": self._ticket_id,
                "order_id": self._order_id,
                "customer": random.choice(["Alex M.", "Jordan P.", "Sam K.", "Riley T.", "Morgan L."]),
                "issue": f"Where is my {delayed_name.lower()}? The tracking hasn't updated in {days_late} days and I really need it!"
            }
        ]

        # --- Task 3: Competitor undercutting on a random product ---
        competitor_candidates = [p for p in product_ids if p != self._out_of_stock_product]
        self._competitor_product = random.choice(competitor_candidates)
        cost = inventory[self._competitor_product]["cost_price"]
        # Competitor price is between cost / 0.8 (the minimum viable margin price) and current retail
        min_viable = round(cost / 0.80, 2)
        current_retail = inventory[self._competitor_product]["retail_price"]
        lower_bound = min_viable + 1.0
        upper_bound = current_retail - 1.0
        if lower_bound >= upper_bound:
            # Fallback: set competitor price slightly below current retail
            self._competitor_price = round(current_retail * 0.90, 2)
        else:
            self._competitor_price = round(random.uniform(lower_bound, upper_bound), 2)

        competitor_data = [
            {"product_id": self._competitor_product, "competitor_price": self._competitor_price}
        ]

        self.state_data = {
            "inventory": inventory,
            "supplier_inbox": supplier_inbox,
            "customer_tickets": customer_tickets,
            "competitor_data": competitor_data
        }

        return self.state()

    def state(self):
        """Returns the current state of the business as a formatted JSON string."""
        return json.dumps(self.state_data, indent=2)

    def _evaluate_reward_and_done(self, action_string):
        """Calculates step-level reward and checks if the episode is complete."""
        reward = 0.0

        # --- Task 1 check: Did the agent zero out the correct product? ---
        oos_stock = self.state_data["inventory"].get(self._out_of_stock_product, {}).get("stock", -1)
        if oos_stock == 0 and "task1" not in self._tasks_solved:
            self._tasks_solved.add("task1")
            reward += 1.0

        # --- Task 2 check: Did the agent issue a refund AND reply to the ticket? ---
        refunds = self.state_data.get("refunds_issued", [])
        replies = self.state_data.get("ticket_replies", [])
        refund_ok = any(r.get("ticket_id") == self._ticket_id and r.get("percentage", 0) >= 15 for r in refunds)
        reply_ok = any(r.get("ticket_id") == self._ticket_id for r in replies)
        if refund_ok and reply_ok and "task2" not in self._tasks_solved:
            self._tasks_solved.add("task2")
            reward += 1.0
        elif (refund_ok or reply_ok) and "task2_partial" not in self._tasks_solved:
            self._tasks_solved.add("task2_partial")
            reward += 0.5

        # --- Task 3 check: Correct competitive pricing with margin ---
        prod_data = self.state_data["inventory"].get(self._competitor_product, {})
        new_price = prod_data.get("retail_price", 999)
        cost = prod_data.get("cost_price", 0)
        target_max = round(self._competitor_price * 0.95, 2)
        min_margin_price = round(cost / 0.80, 2)
        if min_margin_price <= new_price <= target_max and "task3" not in self._tasks_solved:
            self._tasks_solved.add("task3")
            reward += 1.0

        # --- Penalty for invalid actions ---
        if action_string and "error" in action_string.lower():
            reward -= 0.1

        # --- Done when all 3 core tasks are solved ---
        all_done = {"task1", "task2", "task3"}.issubset(self._tasks_solved)

        return reward, all_done

    def step(self, action_string):
        """Parses the AI's action, updates the environment, and returns reward/done."""
        action_string = action_string.strip()

        info = {"error": None, "message": "Action executed successfully."}

        try:
            if action_string.startswith("update_inventory"):
                args = action_string.replace("update_inventory(", "").replace(")", "").split(",")
                prod_id = args[0].strip().strip("'").strip('"')
                new_stock = int(args[1].strip())

                if prod_id in self.state_data["inventory"]:
                    self.state_data["inventory"][prod_id]["stock"] = new_stock
                else:
                    info["error"] = "Product ID not found."

            elif action_string.startswith("issue_refund"):
                args = action_string.replace("issue_refund(", "").replace(")", "").split(",")
                ticket_id = args[0].strip().strip("'").strip('"')
                percentage = int(args[1].strip())

                if "refunds_issued" not in self.state_data:
                    self.state_data["refunds_issued"] = []
                self.state_data["refunds_issued"].append({"ticket_id": ticket_id, "percentage": percentage})

            elif action_string.startswith("update_price"):
                args = action_string.replace("update_price(", "").replace(")", "").split(",")
                prod_id = args[0].strip().strip("'").strip('"')
                new_price = float(args[1].strip())

                if prod_id in self.state_data["inventory"]:
                    self.state_data["inventory"][prod_id]["retail_price"] = new_price
                else:
                    info["error"] = "Product ID not found."

            elif action_string.startswith("reply_ticket"):
                args = action_string.replace("reply_ticket(", "").replace(")", "").split(",")
                ticket_id = args[0].strip().strip("'").strip('"')
                message = ",".join(args[1:]).strip().strip("'").strip('"')

                if "ticket_replies" not in self.state_data:
                    self.state_data["ticket_replies"] = []
                self.state_data["ticket_replies"].append({"ticket_id": ticket_id, "message": message})

            elif action_string == "noop()":
                info["message"] = "No operation performed."

            else:
                info["error"] = "Invalid action syntax."

        except Exception as e:
            info["error"] = f"Failed to parse action: {str(e)}"

        reward, done = self._evaluate_reward_and_done(action_string if info["error"] else "")

        return self.state(), reward, done, info
