"""
API routes for PDF Summarizer.
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse

from models.schemas import (
    DocumentResponse,
    DocumentListResponse,
    SummaryResponse,
    SummaryType,
    DocumentStatus,
)
from services.service import pdf_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Documents"])


@router.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a PDF document",
    description="Upload a PDF file for processing and summarization",
)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document.

    - **file**: PDF file to upload (max 16MB)
    - Returns document metadata including ID and processing status
    """
    try:
        # Read file content
        content = await file.read()

        # Upload document
        document = await pdf_service.upload_document(
            filename=file.filename, content=content
        )

        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            uploaded_at=document.uploaded_at,
            status=document.status,
            page_count=document.page_count,
            word_count=document.word_count,
            file_path=document.file_path,
            error_message=document.error_message,
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}",
        )


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    summary="List all documents",
    description="Get a list of all uploaded documents",
)
async def list_documents():
    """
    List all documents.

    - Returns list of all documents with their metadata
    """
    try:
        documents = pdf_service.list_documents()

        return DocumentListResponse(
            documents=[
                DocumentResponse(
                    id=doc.id,
                    filename=doc.filename,
                    uploaded_at=doc.uploaded_at,
                    status=doc.status,
                    page_count=doc.page_count,
                    word_count=doc.word_count,
                    file_path=doc.file_path,
                    error_message=doc.error_message,
                )
                for doc in documents
            ],
            total=len(documents),
        )

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}",
        )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
    summary="Get document details",
    description="Get detailed information about a specific document",
)
async def get_document(document_id: int):
    """
    Get document details.

    - **document_id**: ID of the document
    - Returns document metadata
    """
    try:
        document = pdf_service.get_document(document_id)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found",
            )

        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            uploaded_at=document.uploaded_at,
            status=document.status,
            page_count=document.page_count,
            word_count=document.word_count,
            file_path=document.file_path,
            error_message=document.error_message,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}",
        )


@router.post(
    "/documents/{document_id}/summarize",
    summary="Generate document summary",
    description="Generate a summary for a document (streaming response)",
)
async def generate_summary(
    document_id: int, summary_type: SummaryType = SummaryType.MEDIUM
):
    """
    Generate a summary for a document.

    - **document_id**: ID of the document to summarize
    - **summary_type**: Type of summary (short, medium, detailed)
    - Returns streaming response with generated summary
    """
    try:
        document = pdf_service.get_document(document_id)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found",
            )

        if document.status != DocumentStatus.READY:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Document {document_id} is not ready for summarization. Status: {document.status}",
            )

        async def generate():
            """Generate and stream the summary."""
            try:
                async for chunk in pdf_service.generate_summary(
                    document_id, summary_type
                ):
                    yield chunk
            except Exception as e:
                logger.error(f"Error generating summary: {e}")
                yield f"\n\nError: {str(e)}"

        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in summarize endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}",
        )


@router.get(
    "/documents/{document_id}/summary",
    response_model=SummaryResponse,
    summary="Get document summary",
    description="Get the latest generated summary for a document",
)
async def get_summary(document_id: int):
    """
    Get the latest summary for a document.

    - **document_id**: ID of the document
    - Returns the most recent summary
    """
    try:
        document = pdf_service.get_document(document_id)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found",
            )

        summary = pdf_service.get_summary(document_id)

        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No summary found for document {document_id}",
            )

        return SummaryResponse(
            id=summary.id,
            document_id=summary.document_id,
            summary_type=summary.summary_type,
            summary_text=summary.summary_text,
            word_count=summary.word_count,
            tokens_used=summary.tokens_used,
            created_at=summary.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}",
        )


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
    description="Delete a document and its associated data",
)
async def delete_document(document_id: int):
    """
    Delete a document.

    - **document_id**: ID of the document to delete
    - Returns 204 No Content on success
    """
    try:
        success = pdf_service.delete_document(document_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found",
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}",
        )
