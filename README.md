# Enhanced Q&A Chatbot

An interactive question-and-answer chatbot built with Streamlit, LangChain, and Groq. Users can select an AI model and adjust the temperature and maximum response length from the sidebar.

## Features

- Simple Streamlit chat interface
- Groq-powered language model responses
- Adjustable temperature
- Adjustable maximum response tokens
- LangChain prompt and output parsing
- Optional LangSmith tracing

## Tech Stack

- Python
- Streamlit
- LangChain
- LangChain Groq
- Groq API
- LangSmith (optional)

## Project Structure

```text
QNA CHATBOT/
├── app.py
├── requirements.txt
├── .env
└── README.md
```

## Local Setup

1. Clone or download this repository.

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=QNA Chatbot
```

`LANGCHAIN_API_KEY` is optional. Never commit `.env` or expose your API keys publicly.

5. Start the application:

```bash
streamlit run app.py
```

The application will open in your browser at the local Streamlit URL.

## Deployment on Streamlit Community Cloud

1. Push `app.py`, `requirements.txt`, and `README.md` to GitHub.
2. Do not upload `.env` or the `venv` folder.
3. Open [Streamlit Community Cloud](https://share.streamlit.io/).
4. Connect your GitHub repository and select `app.py` as the entry point.
5. Add the following values under **Advanced settings → Secrets**:

```toml
GROQ_API_KEY = "your_groq_api_key"
LANGCHAIN_API_KEY = "your_langchain_api_key"
LANGCHAIN_TRACING_V2 = "true"
LANGCHAIN_PROJECT = "QNA Chatbot"
```

6. Click **Deploy**.

## Usage

Enter a question in the input box, adjust the response settings if required, and submit the question to receive an AI-generated answer.

## License

This project is intended for learning and demonstration purposes.
