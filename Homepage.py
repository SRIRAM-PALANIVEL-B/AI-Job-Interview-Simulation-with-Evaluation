import streamlit as st
from secret_key import openapi_key  # Make sure this file exists and contains the API key
import os
from langchain.llms import OpenAI
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain

st.set_page_config(page_icon='rex.png', layout='wide', page_title='Interview Preparation : Getting Started')

st.sidebar.markdown("Navigate using the options above")

# Set the OpenAI API key
if "openai_key" not in st.session_state:
    st.session_state.openai_key = openapi_key

os.environ['OPENAI_API_KEY'] = st.session_state.openai_key
llm = OpenAI()

st.title("Interview AI Tool : Getting Started")
st.header("Recommended Steps : ")

st.markdown("""\n1. Please upload your **resume** in the sidebar on your **left**.
               \n\n2. If you are applying for a specific job, please add **job description** in the text box **below**.
               \n\n3. For starters, we recommend navigating to the **Introduction Round**, where your AI assistant will debrief you
                on the interview and answer your queries related to the interview.
               \n\n4. Next, we recommend having a go with a low stakes **Warmup Round** to get you in the right flow for the 
               actual interview round.
               \n\n5. Navigate to the **Interview Round** to get started with your practice interviews.\n\n""")

st.sidebar.header("Resume")
resume = st.sidebar.file_uploader(label="**Upload your Resume/CV PDF file**", type='pdf')

if resume:
    pdf = PdfReader(resume)

    text = ""
    for page in pdf.pages:
        text += page.extract_text()

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    embeddings = OpenAIEmbeddings()

    try:
        # Create the FAISS vector store from the text chunks and embeddings
        doc = FAISS.from_texts(chunks, embeddings)
    except Exception as e:
        # Handle the error, log it, and inform the user
        st.error("Error occurred while generating embeddings. Please check your API key and internet connection.")
        st.write("Error details:", str(e))
        st.stop()

    chain = load_qa_chain(llm, chain_type="stuff")

    try:
        name = chain.run(input_documents=doc.similarity_search("What is the person's name?"), question="What is the person's name")
        skills = chain.run(input_documents=doc.similarity_search("What are the person's skills?"), question="What are the person's skills?")
    except Exception as e:
        st.error("Error occurred while processing the resume information.")
        st.write("Error details:", str(e))
        st.stop()

    resume_info = {
        "Name": name,
        "Skills": skills
    }

    st.session_state["Resume Info"] = resume_info
    st.sidebar.info("PDF Read Successfully!")

st.header("Job Details")
st.session_state["Job Description"] = st.text_area(label="**Write your job description here**", height=300)
