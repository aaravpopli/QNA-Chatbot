import streamlit as st
import groq
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

import os
from dotenv import load_dotenv
load_dotenv()

## Langsmith tracking

os.environ['LANGCHAIN_API_KEY']=os.getenv('LANGCHAIN_API_KEY')
os.environ['LANGCHAIN_TRACING_V2']='true'
os.environ['LANGCHAIN_PROJECT']='QNA Chatbot'

## Prompt Template

prompt=ChatPromptTemplate.from_messages(
    [
        ('system','You are an helpful assistant. Please response to the user queries'),
        ('user','Question:{question}')
    ]
)

def generate_response(question,llm,temperature,max_tokens):
    llm = ChatGroq(
        model=llm,
        temperature=temperature,
        max_tokens=max_tokens
    )
    output_parser=StrOutputParser()
    chain=prompt|llm|output_parser
    answer=chain.invoke({'question':question})
    return answer

## #Title of the app
st.title("Enhanced Q&A Chatbot With AI")

# Select model
llm = st.sidebar.selectbox("Select Groq model",["openai/gpt-oss-120b"])

## Adjust response parameter
temperature=st.sidebar.slider("Temperature",min_value=0.0,max_value=1.0,value=0.7)
max_tokens = st.sidebar.slider("Max Tokens", min_value=50, max_value=300, value=150)

## MAin interface for user input
st.write("Goe ahead and ask any question")
user_input=st.text_input("You:")

if user_input:
    response=generate_response(user_input,llm,temperature,max_tokens)
    st.write(response)

else:
    st.write("Please provide the user input")


