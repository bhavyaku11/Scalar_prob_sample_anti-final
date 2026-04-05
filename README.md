---
title: Dropshipping Operations Manager
emoji: 📦
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 📦 Dropshipping Operations Manager (OpenEnv)

## Overview
The **Dropshipping Operations Manager** is a text-based, multi-step simulation environment built for the OpenEnv framework. In this simulation, an LLM agent acts as the operations lead for an e-commerce storefront. The agent must parse incoming data from multiple streams (suppliers, customers, and competitors) and execute precise business actions to maintain profitability and customer satisfaction.

## Observation Space (State)
The environment state is returned as a strict JSON dictionary containing four primary keys:
* `inventory`: Current product catalog, stock levels, and retail pricing.
* `supplier_inbox`: Automated emails from suppliers regarding stock shortages or shipments.
* `customer_tickets`: Support tickets from buyers requesting refunds or complaining about delays.
* `competitor_data`: Web-scraped pricing metrics from rival storefronts.

## Action Space
The agent must output exactly one of the following five actions as a string per step. Any malformed action or hallucinated parameter will be gracefully caught and converted to a `noop()`.

1. `update_inventory("PROD_ID", new_stock_int)`: Updates the internal stock ledger based on supplier emails.
2. `issue_refund("TICK_ID", percentage_int)`: Processes a financial refund to resolve a customer complaint (e.g., 15 for a 15% refund).
3. `update_price("PROD_ID", new_price_float)`: Adjusts the retail price of a product to maintain a competitive edge.
4. `reply_ticket("TICK_ID")`: Sends a generic confirmation reply to close a customer support ticket.
5. `noop()`: Takes no action and advances the environment step.

## Evaluation & Graders
The environment evaluates the agent's performance across 5 maximum steps using strict, deterministic Python graders:

* **Task 1 (Easy - Inventory Sync):** The agent must read a supplier email stating a product is out of stock and update `PROD_001` stock to `0`.
* **Task 2 (Medium - Customer Resolution):** The agent must read a customer complaint (`TICK_882`), issue exactly a 15% refund, and reply to the ticket.
* **Task 3 (Hard - Dynamic Pricing):** The agent must read competitor data showing a rival priced at $28.00 and undercut them by exactly 5% (updating `PROD_003` to $26.60).
