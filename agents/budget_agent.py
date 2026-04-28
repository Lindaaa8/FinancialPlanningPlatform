from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, create_react_agent
from langchain_aws import ChatBedrockConverse
from tools.financial_tools import calculate_retirement_corpus, assess_risk_profile

model = ChatBedrockConverse(
    model_id = "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    temperature=0.3,
    max_tokens=4096,
    regions = "us_east_1"
)

budget_tools = [calculate_retirement_corpus, assess_risk_profile]
budget_agent = create_react_agent(
    model=model,
    tools = budget_tools,
    name = "budget_agent",
    prompt = """You are a financial planning expert specializing in retirement and investment planning
    Use the available tools to:
    1. Calculate required retirement corpus based on user's monthly expenses
    2. Assess risk profile and recommend asset allocation
    3. Provide actionable financial advice
    
    Always show your calculations and explain assumptions clearly.
    """)

def build_budget_subgraph():
    workflow = StateGraph(MessagesState)
    workflow.add_node("budget_agent", budget_agent)
    workflow.add_edge(START, "budget_agent")
    workflow.add_edge("budget_agent", END)
    return workflow.compile()