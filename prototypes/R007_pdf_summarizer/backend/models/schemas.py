"""
Pydantic schemas for PDF Summarizer API.
"""
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SummaryType(str, Enum):
    """Types of summary generation."""
    SHORT = "short"
    MEDIUM = "medium"
    DETAILED = "detailed"


class DocumentStatus(str, Enum):
    """Document processing status."""
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


# Request Schemas
class DocumentUpload(BaseModel):
    """Schema for document upload request."""
    filename: str = Field(..., description="Name of the uploaded file")
    content: bytes = Field(..., description="File content as bytes")


class SummaryRequest(BaseModel):
    """Schema for summary generation request."""
    document_id: int = Field(..., description="ID of the document to summarize")
    summary_type: SummaryType = Field(
        default=SummaryType.MEDIUM,
        description="Type of summary to generate"
    )


# Response Schemas
class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: int
    filename: str
    uploaded_at: datetime
    status: DocumentStatus
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for list of documents."""
    documents: list[DocumentResponse]
    total: int


class SummaryResponse(BaseModel):
    """Schema for summary response."""
    id: int
    document_id: int
    summary_type: SummaryType
    summary_text: str
    word_count: int
    tokens_used: int
    created_at: datetime

    class Config:
        from_attributes = True


class SummaryStreamChunk(BaseModel):
    """Schema for streaming summary chunk."""
    chunk: str
    done: bool = False


# Error Schemas
class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: str
    detail: Optional[str] = None
    status_code: int


# Internal Models (for data storage)
class Document:
    """Internal document model."""
    def __init__(
        self,
        id: int,
        filename: str,
        file_path: str,
        status: DocumentStatus = DocumentStatus.PROCESSING
    ):
        self.id = id
        self.filename = filename
        self.file_path = file_path
        self.status = status
        self.uploaded_at = datetime.now()
        self.page_count: Optional[int] = None
        self.word_count: Optional[int] = None
        self.extracted_text: Optional[str] = None
        self.error_message: Optional[str] = None


class Summary:
    """Internal summary model."""
    def __init__(
        self,
        id: int,
        document_id: int,
        summary_type: SummaryType,
        summary_text: str,
        tokens_used: int
    ):
        self.id = id
        self.document_id = document_id
        self.summary_type = summary_type
        self.summary_text = summary_text
        self.tokens_used = tokens_used
        self.word_count = len(summary_text.split())
        self.created_at = datetime.now()
