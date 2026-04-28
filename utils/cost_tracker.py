from langgraph.checkpoint.sqlite import SqliteSaver
from supervisor import build_financial_workflow
from langgraph.checkpoint.memory import InMemorySaver
import time

class CostTracker:
    def __init__(self):
        self.total_cost = 0
        self.input_price_per_1k = 0.003
        self.output_price_per_1k = 0.015
    
    def add_usage(self, input_tokens: int, output_tokens: int):
        cost = (input_tokens/1000) * self.input_price_per_1k + (output_tokens/1000) * self.output_price_per_1k
        self.total_cost += cost
        return cost

checkpointer = InMemorySaver()
cost_tracker = CostTracker()
app = build_financial_workflow()
app_with_memory = app.compile(checkpointer = checkpointer)
config = {"configurable": {"thread_id": "user-session-123"}}