# PDF Summarizer Backend

FastAPI backend for PDF document processing and AI-powered summarization.

## Features

- **PDF Upload & Processing**: Upload PDF files and extract text content
- **Document Metadata**: Track page count, word count, and processing status
- **AI Summarization**: Generate summaries using LLM (Ollama integration)
- **Streaming Responses**: Real-time summary generation
- **RESTful API**: Complete CRUD operations for documents and summaries

## Tech Stack

- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and settings management
- **pdfplumber**: PDF text extraction
- **Pillow**: Image processing for PDFs
- **Ollama**: Local LLM integration (optional)

## Installation

### Prerequisites

- Python 3.11+
- pip or poetry

### Setup

```bash
# Using scripts
./scripts/dev.sh

# Or manually
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Configuration

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Key configuration options:

- `PORT`: Server port (default: 8007)
- `UPLOAD_DIR`: Directory for uploaded PDFs
- `OLLAMA_BASE_URL`: URL for Ollama LLM service
- `MAX_FILE_SIZE`: Maximum file size in bytes

## Running the Server

```bash
# Using script
./scripts/run.sh

# Or directly
python main.py
```

The API will be available at `http://localhost:8007`

Interactive API documentation: `http://localhost:8007/docs`

## API Endpoints

### Documents

- `POST /api/v1/documents` - Upload a PDF
- `GET /api/v1/documents` - List all documents
- `GET /api/v1/documents/{id}` - Get document details
- `DELETE /api/v1/documents/{id}` - Delete a document

### Summaries

- `POST /api/v1/documents/{id}/summarize` - Generate summary (streaming)
- `GET /api/v1/documents/{id}/summary` - Get latest summary

## Testing

```bash
# Run all tests
./scripts/test.sh

# Or with pytest
pytest tests/ -v
```

## Project Structure

```
backend/
├── api/
│   ├── __init__.py
│   └── routes.py          # API endpoint definitions
├── config/
│   ├── __init__.py
│   └── settings.py        # Application configuration
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic models
├── services/
│   ├── __init__.py
│   └── service.py         # Business logic
├── tests/
│   ├── __init__.py
│   └── test_api.py        # API tests
├── data/
│   └── uploads/           # Uploaded PDFs
├── scripts/
│   ├── dev.sh            # Development setup
│   ├── run.sh            # Run server
│   └── test.sh           # Run tests
├── main.py               # Application entry point
├── pyproject.toml        # Dependencies
└── .env.example          # Environment template
```

## PDF Processing

The service uses `pdfplumber` for text extraction:

- Supports multi-page PDFs
- Extracts text content while preserving structure
- Handles various PDF formats
- Cleans and normalizes extracted text

## LLM Integration

The service includes a placeholder for Ollama LLM integration. To enable:

1. Install Ollama: `https://ollama.com`
2. Pull a model: `ollama pull llama2`
3. Uncomment `httpx` in `pyproject.toml`
4. Update the `_stream_llm_response` method in `services/service.py`

## Development

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## License

MIT License - See LICENSE file for details
