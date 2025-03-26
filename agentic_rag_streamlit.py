# import basics
import os
from dotenv import load_dotenv

# import Streamlit
import streamlit as st

# import langchain
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain.agents import create_tool_calling_agent
from langchain import hub
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool

# import Supabase database
from supabase.client import Client, create_client

# load environment variables
load_dotenv()  

# initiate Supabase database
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# initiate embeddings model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# initiate vector store
vector_store = SupabaseVectorStore(
    embedding=embeddings,
    client=supabase,
    table_name="documents",
    query_name="match_documents",
)
 
# initiate OpenAI GPT-4o LLM
llm = ChatOpenAI(model="gpt-4o",temperature=0)

# pull prompt from Langchain hub
prompt = hub.pull("hwchase17/openai-functions-agent")


# create retriever tool
@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

# combine all tools
tools = [retrieve]

# initiate the agent
agent = create_tool_calling_agent(llm, tools, prompt)

# create agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# initiate streamlit app
st.set_page_config(page_title="Agentic RAG Chatbot")
st.title("Agentic RAG Chatbot")

# initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# display chat messages from history on app rerun
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)


# create the bar for user input
user_question = st.chat_input("How are you?")


# if prompt is input by user
if user_question:

    # add the prompt from user to the screen with Streamlit
    with st.chat_message("user"):
        st.markdown(user_question)

        st.session_state.messages.append(HumanMessage(user_question))


    # invoke the agent
    result = agent_executor.invoke({"input": user_question, "chat_history":st.session_state.messages})

    ai_message = result["output"]

    # add the response from the LLM to screen and chat history
    with st.chat_message("assistant"):
        st.markdown(ai_message)

        st.session_state.messages.append(AIMessage(ai_message))
