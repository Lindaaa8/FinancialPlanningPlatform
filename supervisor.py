from typing import Annotated, Literal
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command, Send
from langchain_core.tools import InjectedToolCallId
from langgraph.prebuilt import InjectedState, create_react_agent
from langchain_core.tools import tool
from langchain_aws import ChatBedrockConverse
from langgraph.checkpoint.memory import InMemorySaver
from agents.budget_agent import build_budget_subgraph
from agents.investment_agent import build_investment_subgraph

# Define shared application state
class AppState(MessagesState):
    result: dict # Store outputs from specialized agents
    active_agent: str # Track current agent

# Create handoff tools for agent swtiching
def make_handoff_tool(agent_name: str, agent_description: str):
    @tool(f"transfer_to_{agent_name}", description=f"Transfer conversation to {agent_name}. {agent_description}")
    def handoff_tool(task_description: Annotated[str, "Detailed description of what the agent should do"],
                     state: Annotated[AppState, InjectedState],
                    #  tool_call_id: Annotated[str, InjectedToolCallId]
                    ) -> Command:
        """Transfer control to a specialized agent"""
        return Command(
            goto=agent_name,
            graph=Command.PARENT,
            update={
                "message": state["message"],
                "active_agent": agent_name,
                "task_description": task_description
            }
        )
    return handoff_tool
# Intialize supervisor model
supervisor_model = ChatBedrockConverse(
    model_id = "global.anthropic.claude-sonnet-4-5-20250929-v1:0", 
    temperature=0.2,
    max_tokens = 4096
)

# Create handoff tools
transfer_to_budget = make_handoff_tool(
    "budget_agent",
    "Handles retirement planning, expense analysis, and goal setting"
)
transfer_to_investment = make_handoff_tool(
    "investment_agent", "Handle DSF valuation, stock analysis, and portfolio recommendations"
)

supervisor_agent = create_react_agent(
    model = supervisor_model,
    tools = [transfer_to_budget, transfer_to_investment],
    name = "supervisor",
    prompt = """You are a financial planning supervisor coordinating specialized agents.
     
    ROUTING RULES:
    - Use transfer_to_budget_agent for: retirement planning, expenses, savings goals, corpus calculation
    - Use transfer_to_investment_agent for: stock valuation, DCF, returns analysis, portfolio allocation
    
    Do NOT answer financial questions directly - always route to the appropriate specialist.
    """
)

def build_financial_workflow():
    budget_subgraph = build_budget_subgraph()
    investment_subgraph = build_investment_subgraph()
    workflow = StateGraph(AppState)
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("budget_agent", budget_subgraph)
    workflow.add_node("investment_agent", investment_subgraph)
    # Add conditional edges from supervisor based on handoff
    workflow.add_edge(START, "supervisor")
    workflow.add_edge("budget_agent", END)
    workflow.add_edge("investment_agent", END)
    return workflow.compile()

# checkpointer = InMemorySaver()
app = build_financial_workflow()

def build_financial_workflow_with_memory():
    budget_subgraph = build_budget_subgraph()
    investment_subgraph = build_investment_subgraph()
    workflow = StateGraph(AppState)
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("budget_agent", budget_subgraph)
    workflow.add_node("investment_agent", investment_subgraph)
    workflow.add_edge(START, "supervisor")
    workflow.add_edge("budget_agent", END)
    workflow.add_edge("investment_agent", END)
    return workflow.compile(checkpointer=InMemorySaver())
app_with_memory = build_financial_workflow_with_memory()
config = {"configurable": {"thread_id": "default-session"}}

