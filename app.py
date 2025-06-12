import streamlit as st
import os
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from prompts.system_prompt import get_system_prompt
from dotenv import load_dotenv
load_dotenv()

# Set page config
st.set_page_config(
    page_title="AI Chat Assistant (Internal PDF RAG)",
    page_icon="🤖",
    layout="wide"
)

# --- Simple Password Protection ---
PASSWORD = os.environ.get("APP_PASSWORD", "changeme")

def login():
    st.title("🔒 Login Required")
    pw = st.text_input("Password", type="password")
    if pw == PASSWORD:
        st.session_state["authenticated"] = True
        st.success("Logged in!")
        st.experimental_rerun()
    elif pw:
        st.error("Incorrect password")

if "authenticated" not in st.session_state:
    login()
    st.stop()
# --- End Password Protection ---

st.title("🤖 AI Chat Assistant (Internal PDF RAG)")

CHROMA_PATH = "chroma_db"

# Language selector
language = st.radio("Choose the language for the assistant's answers:", ["English", "German"], horizontal=True)

# Check if vectorstore exists
if not os.path.exists(CHROMA_PATH) or len(os.listdir(CHROMA_PATH)) == 0:
    st.error(f"Vectorstore not found in '{CHROMA_PATH}'. Please run 'python scripts/build_vectorstore.py' to build it from your PDFs.")
    st.stop()

# Load vectorstore and retriever
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
retriever = vectorstore.as_retriever()

st.success("Knowledge base loaded from internal PDFs!")

# Session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Custom CSS for better chat UI
st.markdown("""
<style>
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
        color: white;
    }
    .chat-message.assistant {
        background-color: #f0f2f6;
    }
    .chat-message .content {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
    }
    .chat-message .avatar {
        width: 2rem;
        height: 2rem;
        margin-right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input and RAG response
if prompt := st.chat_input("Ask a question about your internal documents..."):
    # Regenerate system prompt and prompt template with current language
    system_prompt = get_system_prompt(output_language=language, extra_instructions=None)
    custom_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=f"""{system_prompt}

Context:
{{context}}

Question:
{{question}}

Answer:"""
    )
    llm = Ollama(model="llama3")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff",
        chain_type_kwargs={"prompt": custom_prompt}
    )
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        result = qa_chain.invoke({"query": prompt})
        answer = result["result"]
        message_placeholder.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer}) 