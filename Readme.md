# Resume Assistant 🤖📝

**An AI-powered conversational platform using vector-based search and FastAPI to help with resume analysis and queries** 

## Table of Contents 📑
- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)
- [Customization](#customization)

## Overview 🎯

This project is a **chatbot platform** that leverages vector-based search and natural language generation to answer queries about Karthikeyan's portfolio and professional background. It features:

1. 📄 **PDF Data Extraction**: Extracts and processes text from a linked PDF document.
2. 🔍 **Vector Embeddings**: Converts document text into embeddings for similarity search.
3. ⚡ **FastAPI Endpoints**: Provides endpoints for querying and refreshing data.
4. 🎭 **Chatbot Persona**: Custom responses styled as Karthikeyan, an ML engineer.

## Tech Stack 💻

- 🐍 **Python**: Core programming language.
- ⚡ **FastAPI**: Framework for building API endpoints.
- 🗄️ **MongoDB**: Database for storing text embeddings and metadata.
- 🔗 **LangChain**: To handle embeddings and document structuring.
- ☁️ **Boto3**: AWS SDK for Python, if any AWS services are needed.
- 🤗 **Hugging Face Embeddings**: For generating text embeddings.
- 💬 **ChatGroq**: For natural language generation based on user queries.
- 🔐 **dotenv**: For managing environment variables securely.

## Project Structure 📁

- 📱 **app.py**: Contains the main functions for PDF data loading, chunking, embedding generation, and MongoDB indexing.
- 📄 **pdf_extractor.py**: Defines PDFWithLinksLoader class to download and process the PDF document, extracting text and hyperlinks.
- 🔍 **query.py**: Implements the query retrieval process and integrates ChatGroq for generating responses.
- 🌐 **api.py**: FastAPI endpoints for querying and refreshing data.

## Setup and Installation ⚙️

### Prerequisites
- 🐍 Python 3.8 or higher
- 🗄️ MongoDB instance (local or remote)
- 🤗 Hugging Face model (`jinaai/jina-embeddings-v2-base-en`)
- 🔑 ChatGroq API access

### Installation

1. **Clone the repository**: 📂
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

2. **Install dependencies**: 📦
```bash
pip install -r requirements.txt
```

3. **Set up environment variables** (see Environment Variables below). 🔐

4. **Run the FastAPI app**: 🚀
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## Usage 📋

### Querying the Chatbot 💬

1. **Send a POST request** to the `/query` endpoint with a JSON body that includes a `message` and a `chatid`.
2. **Authenticate** with HTTP Basic using your API credentials.

Example:
```json
POST /query
{
    "message": "Tell me about Karthikeyan's recent projects.",
    "chatid": "unique-session-id"
}
```

### Refreshing Data 🔄

The `/refresh` endpoint reloads and reprocesses data from the PDF source to MongoDB.

## Endpoints 🛠️

* 📤 `POST /query`: Queries the chatbot with a user message.
* 🔄 `GET /refresh`: Reloads data from the source PDF and refreshes the MongoDB vector index.

## Environment Variables 🔐

Store these in a `.env` file in the root directory:

```env
MONGO_URI=your_mongodb_uri
GROQ=your_chatgroq_api_key
API_USERNAME=your_api_username
API_PASSWORD=your_api_password
```

## Contributing 🤝

If you want to contribute:

1. Fork the repository 🍴
2. Create a new branch (`git checkout -b feature-branch`) 🌿
3. Make your changes ✍️
4. Push to the branch (`git push origin feature-branch`) 🚀
5. Submit a pull request ✅

## License 📜

This project is licensed under the MIT License. See the `LICENSE` file for more information.

## Customization 🔧

You can easily adapt this project for your own resume or portfolio:

1. 📝 Replace the PDF URL in the `/refresh` endpoint with your own GitHub-hosted resume PDF
2. 🎨 Modify the chatbot persona in `query.py` to match your professional profile
3. ⚙️ Adjust the embedding and chunking parameters to optimize for your document's structure
4. 🚀 Deploy and start using your personalized resume assistant!

Example PDF URL modification in `app.py`:
```python
# Change this line to use your resume
PDF_URL = "https://kkarthik3.github.io/K-Karthikeyan.pdf"
```