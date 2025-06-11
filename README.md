# AI Chat Assistant

A Streamlit-based chat application that uses OpenAI's GPT-4 for natural language conversations.

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Running the Application

Run the Streamlit app:
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Features

- Real-time chat interface with GPT-4
- Streaming responses for better user experience
- Persistent chat history during session
- Modern and clean UI

## Future Enhancements

- Integration with self-hosted LLMs (e.g., Llama)
- PDF document processing and analysis
- Tool calling capabilities
- Enhanced privacy features 