# BDM-BUSINESS-DATA-MANAGEMENT-PROJECT
An AI-powered BDM  chatbot that combines document retrieval, vector search, and LLM reasoning to answer business-related queries. The system stores previous answers to optimize performance and reduce repeated AI calls.

# Features
Conversational Interface: Interact with the bot through a web-based chat interface.

Document Retrieval: Retrieves relevant information from a collection of PDF documents.

Chat History: Maintains a history of chat interactions.

Source Referencing: Provides references to the source documents for the answers given

# Project Structure
app.py: Main application file containing the Flask routes and chat logic.

read_documents.py: Reads and processes PDF documents, and creates a vector store for document retrieval.

requirements.txt: Lists the Python dependencies required for the project.

# System Flow Diagram
User Question
   ↓
Supabase (Check Memory)
   ↓ (if not found)
FAISS (Document Retrieval)
   ↓ (if not relevant)
Groq LLaMA3 (Reasoning)
   ↓
Answer Stored in Supabase
   ↓
Returned to User

# Setup Instructions
**Prerequisites**

Python 3.8 or higher

pip (Python package installer)

**Installation**

**Clone the repository:**

https://github.com/kumudmetkar/BDM-BUSINESS-DATA-MANAGEMENT-PROJECT

**Create and activate a virtual environment:**

python -m venv venv

venv\Scripts\activate  

**Install the required dependencies:**

pip install -r requirements.txt

**Set up the database:**

Automatically set up inside the app.py file.

**Configure the API keys and Base URL**

SUPABASE_URL="your_supabase_url_here"
SUPABASE_ANON_KEY="your_anon_key_here"
GROQ_API_KEY: "your_groq_api_key_here"
BASE_URL: "http://127.0.0.1:5000"

Place your PDF documents in the documents directory. (Already setup, if you want new PDFs, for that place them here.)

**Running the Application**

Start the Flask application:

python app.py

Open your web browser and navigate to http://127.0.0.1:5000 to interact with the bot.

Log in using your Google account to access the application.

# Example Queries

- "Summarize the business strategy document"
- "What was discussed earlier about market growth?"
- "Explain this policy in simple terms"
- "What is Flask in Python?"
This proves it handles both document-based and general knowledge.

# Solution Architecture

1️ **Supabase Knowledge Memory**
- Checks if a question has been answered before
- Returns stored answers instantly
- Avoids unnecessary LLM API calls

2️ **FAISS Vector Retrieval**
- Searches business documents using semantic similarity
- Retrieves relevant context from PDFs

3️ **Groq LLaMA3 LLM Reasoning**
- Generates answers only when no prior knowledge exists
- Explains information in human-readable language

4️ **Continuous Learning**
- New answers are stored in Supabase
- System improves automatically over time

# Tech Stack
- **Frontend / UI:** Streamlit
- **LLM Provider:** Groq (LLaMA3-8B-8192)
- **Vector Database:** FAISS
- **Embeddings:** HuggingFace 
- **Backend Database:** Supabase 
- **Language:** Python
