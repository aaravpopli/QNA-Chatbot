import os

import groq
import streamlit as st
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


st.set_page_config(
    page_title="Q&A Studio",
    page_icon=":material/auto_awesome:",
    layout="centered",
    initial_sidebar_state="auto",
)
load_dotenv()

# Community Cloud exposes credentials through st.secrets. Mirror them into
# environment variables so local .env and deployed configuration use one path.
for secret_name in ("GROQ_API_KEY", "LANGCHAIN_API_KEY"):
    if not os.getenv(secret_name) and secret_name in st.secrets:
        os.environ[secret_name] = str(st.secrets[secret_name])

# LangSmith tracing is optional; the interface also works without its API key.
if os.getenv("LANGCHAIN_API_KEY"):
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_PROJECT", "QNA Chatbot")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond to the user's queries."),
        ("user", "Question: {question}"),
    ]
)


def generate_response(question, llm, temperature, max_tokens):
    model = ChatGroq(
        model=llm,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=60,
        max_retries=0,
    )
    chain = prompt | model | StrOutputParser()
    return chain.invoke({"question": question})


def start_new_chat():
    st.session_state.messages = []
    st.session_state.pop("retry_question", None)


def retry_last_question():
    # Remove the failed exchange before submitting the same question again.
    st.session_state.retry_question = st.session_state.messages[-2]["content"]
    st.session_state.messages = st.session_state.messages[:-2]


if "messages" not in st.session_state:
    st.session_state.messages = []

api_key_ready = bool(os.getenv("GROQ_API_KEY", "").strip())

with st.sidebar:
    st.markdown("## :material/auto_awesome: Q&A Studio")
    st.caption("A little curiosity. A clearer answer.")
    st.button(
        "New chat",
        icon=":material/add:",
        type="primary",
        width="stretch",
        disabled=not st.session_state.messages,
        on_click=start_new_chat,
    )

    st.divider()
    st.markdown("### Response settings")
    llm = st.selectbox(
        "AI model",
        ["openai/gpt-oss-120b"],
        format_func=lambda model: "GPT-OSS 120B",
        help="The Groq-hosted model used to answer your questions.",
    )
    temperature = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Lower values favor focused answers. Higher values allow more variety.",
    )
    st.caption("Focused ← → Creative")
    max_tokens = st.slider(
        "Response length limit",
        min_value=50,
        max_value=2048,
        value=150,
        help="Maximum output tokens, including any model reasoning. Increase this if answers are cut short.",
    )
    st.caption(f"Up to {max_tokens:,} tokens · applies to your next question")

    st.divider()
    with st.expander("Tips for better answers", icon=":material/lightbulb:"):
        st.markdown(
            "- Be specific about what you want to learn.\n"
            "- Include relevant context in each question.\n"
            "- Ask for examples, steps, or a short summary."
        )
    st.caption("Built with Streamlit · Powered by Groq")

st.caption(":material/auto_awesome: YOUR EVERYDAY AI ASSISTANT")
st.title("Big questions. Clear answers.")
st.write("Explore an idea, untangle a concept, or get a fresh perspective.")
st.caption("Each question is answered independently. Your chat stays visible during this session.")
st.divider()

if not api_key_ready:
    st.warning(
        "Add GROQ_API_KEY to your .env file and restart the app to start asking questions.",
        icon=":material/key:",
    )

starter_question = None
if not st.session_state.messages:
    st.subheader("What would you like to explore?")
    st.caption("Pick a starting point, or write your own question below.")
    starters = [
        ("Learn something", "Break down a tricky concept.", ":material/school:",
         "Explain generative AI in simple terms with an everyday example."),
        ("Solve a problem", "Work through it step by step.", ":material/code:",
         "Explain how to find duplicates in a Python list, with a short code example."),
        ("Find inspiration", "Give your next idea a head start.", ":material/lightbulb:",
         "Suggest three beginner-friendly AI project ideas and what I would learn from each."),
    ]
    for column, (title, description, icon, question) in zip(st.columns(3), starters):
        with column, st.container(border=True):
            st.markdown(f"### {icon}")
            st.markdown(f"**{title}**")
            st.caption(description)
            if st.button(
                "Try this",
                key=title,
                width="stretch",
                disabled=not api_key_ready,
                help=question,
            ):
                starter_question = question

for message in st.session_state.messages:
    avatar = ":material/person:" if message["role"] == "user" else ":material/auto_awesome:"
    with st.chat_message(message["role"], avatar=avatar):
        if message.get("error"):
            st.error(message["content"], icon=":material/error:")
        else:
            st.markdown(message["content"])

if st.session_state.messages and st.session_state.messages[-1].get("error"):
    st.button(
        "Retry last question",
        icon=":material/refresh:",
        on_click=retry_last_question,
        disabled=not api_key_ready,
    )

user_input = st.chat_input(
    "Ask a question…",
    disabled=not api_key_ready,
    max_chars=10000,
)
question = user_input or starter_question or st.session_state.pop("retry_question", None)

if question and question.strip() and api_key_ready:
    question = question.strip()
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(question)
    with st.chat_message("assistant", avatar=":material/auto_awesome:"):
        error = None
        try:
            with st.spinner("Thinking through your question…"):
                response = generate_response(question, llm, temperature, max_tokens)
            if not response or not response.strip():
                error = "The model returned an empty answer. Increase the response length limit and retry."
        except groq.AuthenticationError:
            error = "The API key was not accepted. Check GROQ_API_KEY in your .env file and restart the app."
        except groq.RateLimitError:
            error = "The model's usage limit has been reached. Wait a moment, then retry your question."
        except (groq.APIConnectionError, groq.APITimeoutError):
            error = "Could not reach the model. Check your connection and retry your question."
        except Exception:
            # Keep raw provider errors and configuration details out of the UI.
            error = "Something went wrong while generating the answer. Please try again."

        st.session_state.messages.append(
            {"role": "assistant", "content": error or response, "error": bool(error)}
        )
    st.rerun()
