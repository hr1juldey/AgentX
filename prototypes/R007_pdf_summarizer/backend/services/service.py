"""
Service layer for PDF Summarizer API.
Handles PDF processing, text extraction, and LLM integration.
"""

import os
import hashlib
from typing import Optional, List, AsyncGenerator
import logging

import pdfplumber
from config.settings import settings
from models.schemas import (
    Document,
    Summary,
    DocumentStatus,
    SummaryType,
)

logger = logging.getLogger(__name__)


class PDFService:
    """Service for PDF processing and summarization."""

    def __init__(self):
        """Initialize the PDF service."""
        self.documents: dict[int, Document] = {}
        self.summaries: dict[int, Summary] = {}
        self.document_id_counter = 0
        self.summary_id_counter = 0

        # Ensure upload directory exists
        os.makedirs(settings.upload_dir, exist_ok=True)

    async def upload_document(self, filename: str, content: bytes) -> Document:
        """
        Upload and process a PDF document.

        Args:
            filename: Name of the uploaded file
            content: File content as bytes

        Returns:
            Document object with metadata

        Raises:
            ValueError: If file is invalid or not a PDF
        """
        # Validate file extension
        if not filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are allowed")

        # Validate file size
        if len(content) > settings.max_file_size:
            raise ValueError(
                f"File size exceeds maximum of {settings.max_file_size} bytes"
            )

        # Generate unique filename
        file_hash = hashlib.md5(content).hexdigest()
        unique_filename = f"{file_hash}_{filename}"
        file_path = os.path.join(settings.upload_dir, unique_filename)

        # Save file to disk
        with open(file_path, "wb") as f:
            f.write(content)

        # Create document object
        self.document_id_counter += 1
        document = Document(
            id=self.document_id_counter,
            filename=filename,
            file_path=file_path,
            status=DocumentStatus.PROCESSING,
        )

        try:
            # Extract text from PDF
            extracted_text, page_count = await self._extract_pdf_text(file_path)

            document.extracted_text = extracted_text
            document.page_count = page_count
            document.word_count = len(extracted_text.split()) if extracted_text else 0
            document.status = DocumentStatus.READY

            logger.info(
                f"Document {document.id} processed successfully: {page_count} pages, {document.word_count} words"
            )

        except Exception as e:
            document.status = DocumentStatus.ERROR
            document.error_message = str(e)
            logger.error(f"Error processing document {document.id}: {e}")

        self.documents[document.id] = document
        return document

    async def _extract_pdf_text(self, file_path: str) -> tuple[str, int]:
        """
        Extract text from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Tuple of (extracted_text, page_count)

        Raises:
            Exception: If PDF cannot be processed
        """
        text_parts = []
        page_count = 0

        try:
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)

                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                extracted_text = "\n\n".join(text_parts)

                # Clean up the text
                extracted_text = self._clean_text(extracted_text)

                return extracted_text, page_count

        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        lines = text.split("\n")
        cleaned_lines = [line.strip() for line in lines if line.strip()]

        # Remove page numbers and headers (basic heuristic)
        cleaned_lines = [
            line for line in cleaned_lines if not line.isdigit() and len(line) > 3
        ]

        return "\n".join(cleaned_lines)

    def get_document(self, document_id: int) -> Optional[Document]:
        """
        Get a document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document object or None
        """
        return self.documents.get(document_id)

    def list_documents(self) -> List[Document]:
        """
        List all documents.

        Returns:
            List of all documents
        """
        return list(self.documents.values())

    async def generate_summary(
        self, document_id: int, summary_type: SummaryType
    ) -> AsyncGenerator[str, None]:
        """
        Generate a summary for a document using LLM.

        Args:
            document_id: ID of the document to summarize
            summary_type: Type of summary to generate

        Yields:
            Chunks of the generated summary

        Raises:
            ValueError: If document not found or not ready
        """
        document = self.get_document(document_id)

        if not document:
            raise ValueError(f"Document {document_id} not found")

        if document.status != DocumentStatus.READY:
            raise ValueError(f"Document {document_id} is not ready for summarization")

        if not document.extracted_text:
            raise ValueError(f"Document {document_id} has no extracted text")

        # Generate summary prompt based on type
        prompt = self._create_summary_prompt(document.extracted_text, summary_type)

        # Stream summary from LLM
        summary_text = ""
        async for chunk in self._stream_llm_response(prompt):
            summary_text += chunk
            yield chunk

        # Save summary
        self.summary_id_counter += 1
        tokens_used = len(summary_text.split()) * 1.3  # Rough estimate

        summary = Summary(
            id=self.summary_id_counter,
            document_id=document_id,
            summary_type=summary_type,
            summary_text=summary_text,
            tokens_used=int(tokens_used),
        )

        self.summaries[summary.id] = summary
        logger.info(f"Summary {summary.id} generated for document {document_id}")

    def _create_summary_prompt(self, text: str, summary_type: SummaryType) -> str:
        """
        Create a prompt for LLM summarization.

        Args:
            text: Text to summarize
            summary_type: Type of summary

        Returns:
            Prompt string
        """
        word_limits = {
            SummaryType.SHORT: settings.summary_short_max_words,
            SummaryType.MEDIUM: settings.summary_medium_max_words,
            SummaryType.DETAILED: settings.summary_detailed_max_words,
        }

        max_words = word_limits[summary_type]

        prompt = f"""Please summarize the following text in approximately {max_words} words.
Focus on the main points, key findings, and important details.

Text to summarize:
{text[:4000]}  # Limit input text for demo

Summary:"""

        return prompt

    async def _stream_llm_response(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Stream response from LLM.

        Args:
            prompt: Prompt to send to LLM

        Yields:
            Response chunks from LLM

        Note:
            This is a placeholder implementation. In production, you would:
            1. Connect to Ollama API
            2. Stream the response
            3. Handle errors and retries
        """
        # Placeholder: Simulate streaming response
        # In production, use httpx to connect to Ollama API
        # Example: POST {settings.ollama_base_url}/api/generate

        placeholder_response = """This is a placeholder summary. In production, this would be generated by the LLM.

To integrate with Ollama:
1. Ensure Ollama is running: ollama serve
2. Install httpx: pip install httpx
3. Use the following code:

```python
import httpx
import json

async with httpx.AsyncClient() as client:
    async with client.stream(
        'POST',
        f'{settings.ollama_base_url}/api/generate',
        json={
            'model': settings.ollama_model,
            'prompt': prompt,
            'stream': True
        },
        timeout=300.0
    ) as response:
        async for line in response.aiter_lines():
            if line:
                data = json.loads(line)
                if 'response' in data:
                    yield data['response']
```

The actual implementation would stream real responses from the LLM model."""

        # Simulate streaming by yielding chunks
        words = placeholder_response.split()
        for i, word in enumerate(words):
            yield word + " "
            if i % 5 == 0:  # Simulate network delay
                import asyncio

                await asyncio.sleep(0.01)

    def get_summary(self, document_id: int) -> Optional[Summary]:
        """
        Get the latest summary for a document.

        Args:
            document_id: Document ID

        Returns:
            Summary object or None
        """
        # Find the most recent summary for this document
        document_summaries = [
            s for s in self.summaries.values() if s.document_id == document_id
        ]

        if not document_summaries:
            return None

        return max(document_summaries, key=lambda s: s.created_at)

    def delete_document(self, document_id: int) -> bool:
        """
        Delete a document and its file.

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        document = self.get_document(document_id)

        if not document:
            return False

        # Delete file from disk
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except Exception as e:
            logger.error(f"Error deleting file {document.file_path}: {e}")

        # Remove from memory
        del self.documents[document_id]

        # Remove associated summaries
        self.summaries = {
            k: v for k, v in self.summaries.items() if v.document_id != document_id
        }

        logger.info(f"Document {document_id} deleted")
        return True


# Singleton instance
pdf_service = PDFService()
