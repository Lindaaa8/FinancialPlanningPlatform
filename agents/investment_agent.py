from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import create_react_agent
from langchain_aws import ChatBedrockConverse
from tools.financial_tools import calculate_dcf_value


model = ChatBedrockConverse(
    model_id = "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    temperature = 0.3,
    max_tokens = 4096,
    regions = "us_east_1"
)
investment_tools = [calculate_dcf_value]

investment_agent = create_react_agent(
    model=model,
    tools = investment_tools,
    name="investment_agent",
    prompt="""You are an investment analysis expert 
    Use the DCF tool to value companies and provide investment recommendation."""
)

def build_investment_subgraph():
    workflow = StateGraph(MessagesState)
    workflow.add_node("investment_agent", investment_agent)
    workflow.add_edge(START, "investment_agent")
    workflow.add_edge("investment_agent", END)
    return workflow.compile()
