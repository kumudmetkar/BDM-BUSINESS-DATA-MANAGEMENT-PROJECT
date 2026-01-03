# version 3 - trying supabase

import os
import streamlit as st
import re
import json
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from supabase import create_client, Client

url = "https://mbwcguispwdchxfiqptg.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1id2NndWlzcHdkY2h4ZmlxcHRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMzMjQ1NzcsImV4cCI6MjA1ODkwMDU3N30.ltbAt2qWyF420qao7BNvz_xR6Hs0i3C21gHD3SIm8Bo"
supabase: Client = create_client(url, key)

os.environ["GROQ_API_KEY"] = "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"

@st.cache_resource
def load_model():
    return ChatGroq(temperature=0.8, model="llama3-8b-8192")

@st.cache_data
def load_hidden_pdfs(directory="hidden_docs"):
    all_texts = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(directory, filename))
            pages = loader.load_and_split()
            all_texts.extend([page.page_content for page in pages])
    return all_texts

@st.cache_resource
def create_vector_store(document_texts):
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.from_texts(document_texts, embedder)

def is_valid_email(email):
    email_regex = r"^[a-zA-Z0-9_.+-]+@gmail\.com$"
    return re.match(email_regex, email) is not None

# Save session data (question and answer pairs) to Supabase
def save_session_to_supabase(email, name, chat_history):
    for question, answer in chat_history:
        data = {
            "email": email,
            "name": name if name else None,
            "question": question,
            "answer": answer,
        }
        # Insert data into Supabase
        response = supabase.table("chat_sessions").insert(data).execute()

        # Check if response has errors (if any)
        if "error" in response:
            st.error(f"Error saving session data to Supabase: {response['error']['message']}")
            return False
    return True
# Function to check Supabase for a previous answer
def check_supabase_for_answer(question):
    response = supabase.table("chat_sessions").select("answer").eq("question", question).execute()
    if response.data:
        return response.data[0]["answer"]  # Return the first matching answer
    return None  # If no answer is found

st.title("BDM Chatbot")
st.write("Ask questions directly based on the preloaded BDM documents.")
st.write("Note - Once your queries are complete, please put the last query as \"stop\".")
st.write("Disclaimer - All data, including questions and answers, is collected for improving the bot’s functionality. By using this bot, you consent to this data being stored.")

model = load_model()
document_texts = load_hidden_pdfs()
vector_store = create_vector_store(document_texts)
retrieval_chain = ConversationalRetrievalChain.from_llm(model, retriever=vector_store.as_retriever(search_kwargs={"score_threshold": 0.7}))

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "email_validated" not in st.session_state:
    st.session_state["email_validated"] = False

email = st.text_input("Enter your email (format: example@gmail.com):")

name = st.text_input("Enter your name (optional):")

if email and is_valid_email(email):
    st.session_state["email_validated"] = True
    st.success("Email validated successfully! You can now ask your questions.")
elif email:
    st.error("Invalid email format. Please enter a valid email.")

if st.session_state["email_validated"]:
    user_input = st.text_input("Pose your Questions:")
    
    if user_input:
        if user_input.lower() == "stop":
            st.write("Chatbot: Goodbye!")
            session_data = {
                "email": email,
                "name": name,
                "chat_history": st.session_state["chat_history"]
            }

            # Save session data to Supabase
            if save_session_to_supabase(email, name, st.session_state["chat_history"]):
                st.success("Session data successfully saved to Supabase!")

            # Allow the user to download session data as JSON when they say "stop"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_data_{timestamp}.json"
            st.download_button(
                label="Download Session Data",
                data=json.dumps(session_data, indent=4), 
                file_name=filename,
                mime="application/json"
            )
        else:
            # Step 1: Check Supabase for the answer
            existing_answer = check_supabase_for_answer(user_input)
            if existing_answer:
                st.session_state["chat_history"].append((user_input, existing_answer))
                st.write(f"Chatbot: {existing_answer}")
            else:
                # Process the question and answer
                response = retrieval_chain.invoke({"question": user_input, "chat_history": st.session_state["chat_history"]})
                answer = response["answer"]
                # Debugging: Log the response from the retrieval chain
                st.write(f"Retrieval Chain Response: {answer}")
                # Step 3: If FAISS has no answer, use Groq AI
                if not answer or "I don't know" in answer.lower():    # 4 indents (16 spaces)
                    answer = model.invoke(user_input)  # 5 indents (20 spaces)

                # Step 4: Store the answer in Supabase
                data = {  # 4 indents (16 spaces)
                    "email": email,  # 5 indents (20 spaces)
                    "name": name if name else None,  # 5 indents (20 spaces)
                    "question": user_input,  # 5 indents (20 spaces)
                    "answer": answer,  # 5 indents (20 spaces)
                    "timestamp": datetime.now().isoformat(),  # 5 indents (20 spaces)
                }  # 4 indents (16 spaces)
                supabase.table("chat_sessions").insert(data).execute()  # 4 indents (16 spaces)
                st.session_state["chat_history"].append((user_input, answer))
                st.write(f"Chatbot: {answer}")
            # Display the chat history
            for i, (question, reply) in enumerate(st.session_state["chat_history"], 1):
                st.write(f"Q{i}: {question}")
                st.write(f"Chatbot: {reply}")


















































