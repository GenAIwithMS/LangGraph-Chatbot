# Agentic Chatbot with LangGraph

A sophisticated chatbot implementation built using LangGraph, featuring a multi-threaded conversation system with persistent storage and various tool integrations.

## Features

- **Multi-threaded Conversations**: Support for multiple chat threads with unique identifiers
- **Persistent Storage**: SQLite backend for storing conversation history
- **Streamlit Frontend**: User-friendly web interface
- **Tool Integration**: Multiple tools for enhanced functionality:
  - Web Search
  - Weather Information
  - Calculator
  - Stock Price Lookup

## Technology Stack

- **Framework**: LangGraph
- **Model**: Groq (OpenAI GPT OSS 120B)
- **Frontend**: Streamlit
- **Database**: SQLite
- **Language**: Python 3.x

## Prerequisites

- Python 3.x
- Environment variables configured (see Configuration section)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/GenAIwithMS/LangGraph-Chatbot
cd LangGraph-Chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root
2. Configure the necessary API keys and environment variables

## Project Structure

- `frontend_with_database.py`: Streamlit frontend implementation
- `database_backend.py`: Backend logic and LangGraph integration
- `tools.py`: Custom tool implementations
- `thread_id_name.py`: Thread management utilities
- `requirements.txt`: Project dependencies

## Running the Application

1. Start the Streamlit server:
```bash
streamlit run frontend_with_database.py
```

2. Open your browser and navigate to the provided local URL (typically http://localhost:8501)

## Features in Detail

### Chat Threads
- Create new chat threads
- Switch between existing threads
- Persistent conversation history
- Automatic thread title generation

### Tool Integration
- Web search capabilities
- Real-time weather information
- Basic calculator functionality
- Stock price lookup

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- LangGraph team for the framework
- Groq for the language model
- Streamlit for the frontend framework

