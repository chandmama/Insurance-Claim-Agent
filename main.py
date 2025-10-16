# main.py
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from tools import tools, tool_map
from schema import SupportOutput

load_dotenv()

# --- Load LLM ---
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.3)

# --- Output Parser ---
parser = PydanticOutputParser(pydantic_object=SupportOutput)

# --- Prompt Template ---

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



# --- Create Agent and Executor ---
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- CLI Chat Loop ---
chat_history = []

print("🤖 Insurance Claim Support Assistant")
print("Type 'exit' to quit | 'end session' to log & clear\n")

while True:
    try:
        user_input = input("Customer: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        chat_history.append(HumanMessage(content=user_input))

        result = executor.invoke({"query": user_input, "chat_history": chat_history})

        try:
            structured = parser.parse(result["output"])
        except Exception:
            print("⚠️ Could not parse structured output. Raw response below:")
            print(result["output"])
            continue

        print("\nAgent:", structured.answer)
        if structured.sources:
            print("Sources:", structured.sources)
        if structured.action_taken:
            print("Action Taken:", structured.action_taken)

        chat_history.append(AIMessage(content=structured.answer))

        if user_input.lower() == "end session":
            transcript = "\n".join([
                f"{'User' if isinstance(msg, HumanMessage) else 'Agent'}: {msg.content}"
                for msg in chat_history
            ])
            tool_map["save_log"].func(transcript)
            chat_history.clear()
            print("📋 Session logged and cleared.\n")

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
