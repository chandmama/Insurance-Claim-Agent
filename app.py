import streamlit as st
import os
import json
import glob
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from tools import tools, tool_map
from schema import SupportOutput

load_dotenv()

# --- LLM & Parser ---
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.3)
parser = PydanticOutputParser(pydantic_object=SupportOutput)

# --- Prompt ---
prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a professional, empathetic, and knowledgeable **Insurance Support Assistant**.

### Core Responsibilities:
1. **Retrieve Information:** Always use the `search_kb` function first to find answers in the insurance FAQ knowledge base.  
2. **Escalate When Needed:** If the requested information is unclear, incomplete, or unavailable, use the `create_ticket` function to escalate the issue to a human representative.  
3. **Maintain Records:** After every interaction, use the `save_log` function to record the conversation summary and resolution status.  
4. **Tone & Style:** Be courteous, concise, and empathetic. Use plain, customer-friendly language while maintaining professionalism and accuracy.

### Response Format:
Respond **only** in the following JSON structure:
{format_instructions}
"""),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
    ("placeholder", "{agent_scratchpad}")
]).partial(format_instructions=parser.get_format_instructions())

# --- Agent Setup ---
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

# --- Streamlit Page ---
st.set_page_config(page_title="Insurance Support Assistant", page_icon="🤖", layout="centered")
st.title("🤖 Insurance Claim Support Assistant")
st.caption("Your virtual insurance helpdesk powered by Gemini + LangChain")

# --- Ensure logs folder exists ---
os.makedirs("logs", exist_ok=True)

# --- Helper: Save session automatically ---
def save_session_to_file():
    filename = st.session_state.get("log_file")
    if not filename:
        filename = datetime.now().strftime("logs/session_%Y%m%d_%H%M%S.json")
        st.session_state.log_file = filename

    transcript = [
        {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
        for msg in st.session_state.chat_history
    ]

    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "messages": transcript
        }, f, indent=2, ensure_ascii=False)

# --- Helper: Load a saved chat session ---
def load_session(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        messages = data.get("messages", [])
        chat_history = []
        for msg in messages:
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            else:
                chat_history.append(AIMessage(content=msg["content"]))
        return chat_history
    except Exception as e:
        st.error(f"⚠️ Could not load session: {e}")
        return []

# --- Load or create session ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "log_file" not in st.session_state:
    st.session_state.log_file = None

# --- Sidebar: Session management ---
with st.sidebar:
    st.header("💬 Chat Sessions")
    saved_sessions = sorted(glob.glob("logs/session_*.json"), reverse=True)

    if saved_sessions:
        selected_session = st.selectbox("📂 Load previous chat:", saved_sessions, index=0)
        if st.button("Load Selected Session"):
            st.session_state.chat_history = load_session(selected_session)
            st.session_state.log_file = selected_session
            st.success(f"Loaded: {selected_session}")

    st.markdown("---")
    if st.button("🧹 Start New Session"):
        st.session_state.chat_history = []
        st.session_state.log_file = None
        st.rerun()

    st.markdown("---")
    st.markdown("💡 **Tips:**\n- Ask specific insurance questions\n- Use plain language\n- Type ‘End & Save Session’ to archive your chat")


# --- Display existing messages ---
for msg in st.session_state.chat_history:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.write(msg.content)

# --- User input ---
user_query = st.chat_input("Ask about your insurance policy, claims, or coverage...")

if user_query:
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    with st.chat_message("user"):
        st.write(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = executor.invoke({"query": user_query, "chat_history": st.session_state.chat_history})
                structured = parser.parse(result["output"])
                st.markdown(structured.answer)
                if structured.sources:
                    with st.expander("📚 Sources"):
                        st.write("\n".join(structured.sources))
                if structured.action_taken:
                    st.info(structured.action_taken)
                st.session_state.chat_history.append(AIMessage(content=structured.answer))
                save_session_to_file()  # ✅ Auto-save after each exchange
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
        
        
