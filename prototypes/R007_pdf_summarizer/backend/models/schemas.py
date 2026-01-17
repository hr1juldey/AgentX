"""
Pydantic schemas for PDF Summarizer API with enhanced Swagger documentation.

This module provides request/response models for PDF document processing
and AI-powered summarization.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Internal data classes (not exposed via API)
class Document(BaseModel):
    """Internal document storage model."""

    id: int
    filename: str
    uploaded_at: datetime
    status: DocumentStatus
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    extracted_text: str = ""

    class Config:
        from_attributes = True


class Summary(BaseModel):
    """Internal summary storage model."""

    id: int
    document_id: int
    summary_type: SummaryType
    summary_text: str
    word_count: int
    tokens_used: int
    created_at: datetime

    class Config:
        from_attributes = True


class SummaryType(str, Enum):
    """Types of summary generation.

    Controls the length and detail level of generated summaries.
    """

    SHORT = "short"
    MEDIUM = "medium"
    DETAILED = "detailed"


class DocumentStatus(str, Enum):
    """Document processing status.

    Tracks the state of document processing pipeline.
    """

    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class DocumentUpload(BaseModel):
    """Schema for document upload request.

    Upload a PDF file for processing and summarization.
    """

    filename: str = Field(
        ...,
        description="Name of the uploaded file",
        examples=["research_paper.pdf", "report.pdf"],
    )
    content: bytes = Field(
        ...,
        description="File content as bytes (use multipart/form-data)",
        examples=["<binary data>"],
    )


class SummaryRequest(BaseModel):
    """Schema for summary generation request.

    Generate an AI summary of an uploaded document.
    """

    document_id: int = Field(
        ..., description="ID of the document to summarize", examples=[1, 42]
    )
    summary_type: SummaryType = Field(
        default=SummaryType.MEDIUM,
        description="Type/length of summary to generate",
        examples=[SummaryType.SHORT, SummaryType.MEDIUM, SummaryType.DETAILED],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{"document_id": 1, "summary_type": "medium"}]
        }
    }


class DocumentResponse(BaseModel):
    """Schema for document response.

    Returns document metadata and processing status.
    """

    id: int = Field(..., description="Unique document identifier", examples=[1, 42])
    filename: str = Field(
        ..., description="Original filename", examples=["research_paper.pdf"]
    )
    uploaded_at: datetime = Field(
        ...,
        description="When the document was uploaded",
        examples=["2024-01-15T10:00:00Z"],
    )
    status: DocumentStatus = Field(
        ..., description="Current processing status", examples=[DocumentStatus.READY]
    )
    page_count: Optional[int] = Field(
        None, description="Number of pages in the document", examples=[15]
    )
    word_count: Optional[int] = Field(
        None, description="Total word count", examples=[5000]
    )
    file_path: Optional[str] = Field(None, description="Storage location of the file")
    error_message: Optional[str] = Field(
        None, description="Error message if processing failed"
    )

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """Schema for list of documents."""

    documents: list[DocumentResponse] = Field(
        default_factory=list, description="List of documents"
    )
    total: int = Field(..., description="Total count of documents", examples=[10])


class SummaryResponse(BaseModel):
    """Schema for summary response.

    Returns the generated summary with metadata.
    """

    id: int = Field(..., description="Unique summary identifier", examples=[1])
    document_id: int = Field(
        ..., description="ID of the summarized document", examples=[1]
    )
    summary_type: SummaryType = Field(
        ...,
        description="Type of summary that was generated",
        examples=[SummaryType.MEDIUM],
    )
    summary_text: str = Field(
        ..., description="Generated summary text", examples=["This paper discusses..."]
    )
    word_count: int = Field(
        ..., description="Word count of the summary", examples=[250]
    )
    tokens_used: int = Field(
        ..., description="AI tokens consumed for generation", examples=[1000]
    )
    created_at: datetime = Field(
        ...,
        description="When the summary was created",
        examples=["2024-01-15T10:05:00Z"],
    )

    model_config = {"from_attributes": True}


class SummaryStreamChunk(BaseModel):
    """Schema for streaming summary chunk.

    Used for real-time summary generation via WebSocket.
    """

    chunk: str = Field(
        ..., description="Partial summary text chunk", examples=["This paper discusses"]
    )
    done: bool = Field(
        default=False,
        description="Whether generation is complete",
        examples=[False, True],
    )


class ErrorResponse(BaseModel):
    """Schema for error response."""

    error: str = Field(
        ..., description="Error type", examples=["ValidationError", "ProcessingError"]
    )
    detail: Optional[str] = Field(None, description="Additional error details")
    status_code: int = Field(
        ..., description="HTTP status code", examples=[400, 404, 500]
    )
