from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class InventoryItem(BaseModel):
    name: str = Field(description="Product name")
    cost_price: float = Field(description="Cost price to source the product")
    retail_price: float = Field(description="Current retail price on the storefront")
    stock: int = Field(description="Current stock quantity")

class SupplierMessage(BaseModel):
    email_id: str = Field(description="Unique email identifier")
    sender: str = Field(alias="from", description="Sender of the email")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Content of the email")

class CustomerTicket(BaseModel):
    ticket_id: str = Field(description="Unique ticket identifier")
    order_id: str = Field(description="Associated order identifier")
    customer: str = Field(description="Customer name")
    issue: str = Field(description="Customer issue description")

class CompetitorData(BaseModel):
    product_id: str = Field(description="Product identifier of the competitor's listing")
    competitor_price: float = Field(description="Competitor's price for the item")

class RefundIssued(BaseModel):
    ticket_id: str = Field(description="Ticket identifier for which refund was issued")
    percentage: int = Field(description="Percentage amount refunded")

class TicketReply(BaseModel):
    ticket_id: str = Field(description="Ticket identifier replied to")
    message: str = Field(description="Message sent to the customer")

class Observation(BaseModel):
    inventory: Dict[str, InventoryItem] = Field(description="Dictionary mapping product IDs to inventory items")
    supplier_inbox: List[SupplierMessage] = Field(description="List of emails received from suppliers")
    customer_tickets: List[CustomerTicket] = Field(description="List of support requests from customers")
    competitor_data: List[CompetitorData] = Field(description="List of pricing data from competitors")
    refunds_issued: Optional[List[RefundIssued]] = Field(default=None, description="List of refunds issued during the episode")
    ticket_replies: Optional[List[TicketReply]] = Field(default=None, description="List of replies sent to customers during the episode")

class Action(BaseModel):
    action_str: str = Field(description="The selected action function call to execute")

class Reward(BaseModel):
    score: float = Field(description="The numeric reward score between 0.0 and 1.0")
