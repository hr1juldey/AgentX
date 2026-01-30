"""Tests for Pydantic-Zod contract alignment between backend and frontend.

Validates that backend Pydantic models have correct field names and types
that match frontend expectations.
"""

import json
from uuid import UUID, uuid4
from datetime import datetime

import pytest

from agentx.domain.entities.enums import UIComponentType
from agentx.ui.descriptors.base import (
    BaseUIDescriptor,
    MarkdownDescriptor,
    CardDescriptor,
)
from agentx.application.dtos.voice_gateway_dtos import (
    ConversationContextDTO,
    ConversationMessageDTO,
)


class TestDescriptorFieldAlignment:
    """Test that descriptors have required fields with correct names."""

    def test_base_descriptor_has_descriptor_id(self) -> None:
        """BaseUIDescriptor must have descriptor_id field."""
        descriptor = MarkdownDescriptor(content="test")
        assert descriptor.descriptor_id is not None
        assert isinstance(descriptor.descriptor_id, UUID)

    def test_base_descriptor_has_component_type(self) -> None:
        """BaseUIDescriptor must have component_type field."""
        descriptor = MarkdownDescriptor(content="test")
        assert descriptor.component_type == UIComponentType.MARKDOWN

    def test_descriptor_serialization(self) -> None:
        """Descriptor should serialize to dict with correct field names."""
        descriptor = CardDescriptor(title="Test", content="Content")
        data = descriptor.to_dict()
        assert "descriptor_id" in data
        assert "component_type" in data
        assert "props" in data
        assert data["props"]["title"] == "Test"

    def test_no_raw_id_field(self) -> None:
        """Descriptors must use 'descriptor_id' not 'id'."""
        descriptor = MarkdownDescriptor(content="test")
        # Should have descriptor_id
        assert hasattr(descriptor, "descriptor_id")
        # to_dict should not have bare 'id' field
        data = descriptor.to_dict()
        assert "id" not in data
        assert "descriptor_id" in data

    def test_type_value_is_lowercase_markdown(self) -> None:
        """UIComponentType.MARKDOWN value should be 'markdown'."""
        assert UIComponentType.MARKDOWN.value == "markdown"


class TestVoiceGatewayDTOAlignment:
    """Test voice gateway DTO field alignment."""

    def test_conversation_message_dto_has_message_id(self) -> None:
        """ConversationMessageDTO must have message_id field."""
        dto = ConversationMessageDTO(
            message_id=str(uuid4()),
            role="user",
            content="Test message",
            timestamp=datetime.now(),
        )
        assert dto.message_id is not None
        assert isinstance(dto.message_id, str)

    def test_conversation_context_dto_entities_is_dict(self) -> None:
        """ConversationContextDTO entities should be a dict."""
        dto = ConversationContextDTO(
            topic="test",
            entities={},
            sentiment="neutral",
        )
        assert isinstance(dto.entities, dict)

    def test_kyutai_message_session_id_alias(self) -> None:
        """KyutaiMessage should have sessionId alias for frontend camelCase."""
        from agentx.application.dtos.voice_gateway_dtos import KyutaiMessage, KyutaiMessageType

        msg = KyutaiMessage(
            type=KyutaiMessageType.TEXT,
            data="test",
            session_id="abc123",
            timestamp=1234567890.0,
        )
        # Should serialize to camelCase
        data = msg.to_dict()
        assert "sessionId" in data
        assert data["sessionId"] == "abc123"

    def test_conversation_context_dto_serialization(self) -> None:
        """ConversationContextDTO should serialize to JSON correctly."""
        dto = ConversationContextDTO(
            topic="test",
            entities={},
            sentiment="neutral",
        )
        json_str = dto.model_dump_json()
        assert json_str is not None
        # Verify JSON is valid
        parsed = json.loads(json_str)
        assert "topic" in parsed or "topic" in str(parsed)


class TestDescriptorCreation:
    """Test descriptor creation and validation."""

    def test_markdown_descriptor_validate(self) -> None:
        """MarkdownDescriptor.validate() should work correctly."""
        descriptor = MarkdownDescriptor(content="Test content")
        assert descriptor.validate() is True

    def test_card_descriptor_validate(self) -> None:
        """CardDescriptor.validate() should work correctly."""
        descriptor = CardDescriptor(title="Title", content="Content")
        assert descriptor.validate() is True

    def test_card_descriptor_validate_empty_title_fails(self) -> None:
        """CardDescriptor with empty title should fail validation."""
        descriptor = CardDescriptor(title="", content="Content")
        assert descriptor.validate() is False
