import json

class DropshippingEnv:
    def __init__(self):
        self.state_data = {}
        self.reset()

    def reset(self):
        """Initializes the mock database for our dropshipping store."""
        self.state_data = {
            "inventory": {
                "PROD_001": {"name": "Wireless Earbuds", "cost_price": 15.00, "retail_price": 39.99, "stock": 150},
                "PROD_002": {"name": "Posture Corrector", "cost_price": 4.50, "retail_price": 19.99, "stock": 85},
                "PROD_003": {"name": "LED Desk Lamp", "cost_price": 12.00, "retail_price": 34.99, "stock": 40}
            },
            "supplier_inbox": [
                {"email_id": "SUP_101", "from": "Shenzhen Audio Factory", "subject": "URGENT: PROD_001 Production Delay", "body": "Due to component shortages, we are completely out of stock for the Wireless Earbuds (PROD_001). We cannot fulfill new orders for 3 weeks."}
            ],
            "customer_tickets": [
                {"ticket_id": "TICK_882", "order_id": "ORD_5591", "customer": "Alex M.", "issue": "Where is my posture corrector? The tracking hasn't updated in 9 days and I need it for my back pain!"}
            ],
            "competitor_data": [
                {"product_id": "PROD_003", "competitor_price": 28.00}
            ]
        }
        return self.state()

    def state(self):
        """Returns the current state of the business as a formatted JSON string."""
        return json.dumps(self.state_data, indent=2)

    def step(self, action_string):
        """Parses the AI's action and updates the environment state."""
        # Clean up the input string just in case the AI added extra spaces
        action_string = action_string.strip()
        
        reward = 0.0
        done = False
        info = {"error": None, "message": "Action executed successfully."}

        try:
            if action_string.startswith("update_inventory"):
                # Extract arguments: update_inventory('PROD_001', 0)
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
                
                # In a real app we'd trigger a payment gateway here.
                # For our simulation, we'll log it in a new 'refunds_issued' key.
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

        return self.state(), reward, done, info