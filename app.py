import streamlit as st
from supervisor import app_with_memory, config

st.title("GoalPilot - AI Financial Planning Assistant")
st.caption("Powered by LangGraph Multi-Agent System + Claude-Sonnect-4-5")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("agent") and msg["role"] == "assistant":
            st.caption(f"🤖 Responded by: **{msg['agent']}**")
    
if prompt := st.chat_input("Ask about retirement planning, investments, or financial goals..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Coordinating financial agents..."):
            response = app_with_memory.invoke({
                "messages": st.session_state.messages
            }, config=config)
            assistant_msg = response["messages"][-1].content
            st.markdown(assistant_msg)
            st.caption(f"Active Agent: {response.get('active_agent', 'Supervisor')}")
            st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
