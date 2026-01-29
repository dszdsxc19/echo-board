"""Data validation checkpoints throughout the Echo-Board workflow."""

import os
from pathlib import Path
from typing import Any, Dict, List

from .logging import EchoBoardLogger
from .models.conversation import ConversationSession
from .models.note import Note

logger = EchoBoardLogger.get_logger("validation")


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class ValidationCheckpoint:
    """Centralized validation checkpoints for the application."""

    @staticmethod
    def validate_user_query(query: str) -> str:
        """Validate user query before processing.

        Args:
            query: User's question

        Returns:
            Validated query string

        Raises:
            ValidationError: Query is invalid
        """
        if not query or not query.strip():
            raise ValidationError("用户查询不能为空")

        if len(query.strip()) < 5:
            raise ValidationError("用户查询太短，请提供更详细的信息")

        if len(query) > 2000:
            raise ValidationError("用户查询太长，请保持在2000字符以内")

        # Check for potentially problematic content
        forbidden_patterns = ["<script", "javascript:", "data:"]
        query_lower = query.lower()
        for pattern in forbidden_patterns:
            if pattern in query_lower:
                raise ValidationError("用户查询包含不允许的内容")

        logger.info(f"Query validation passed: {query[:100]}")
        return query.strip()

    @staticmethod
    def validate_notes(notes: List[Note]) -> List[Note]:
        """Validate loaded notes.

        Args:
            notes: List of loaded notes

        Returns:
            Validated list of notes

        Raises:
            ValidationError: Notes contain invalid data
        """
        if not notes:
            logger.warning("No notes loaded for validation")
            return notes

        valid_notes = []
        for note in notes:
            try:
                # Check required fields
                if not note.title:
                    logger.warning(f"Note missing title: {note.file_path}")
                    continue

                if not note.content or not note.content.strip():
                    logger.warning(f"Note has empty content: {note.file_path}")
                    continue

                # Check file path exists
                if note.file_path and not Path(note.file_path).exists():
                    logger.warning(f"Note file not found: {note.file_path}")
                    continue

                # Validate content size
                if len(note.content) > 10 * 1024 * 1024:  # 10MB
                    logger.warning(f"Note too large, skipping: {note.file_path}")
                    continue

                valid_notes.append(note)

            except Exception as e:
                logger.error(f"Error validating note {note.file_path}: {e}")
                continue

        logger.info(f"Validation passed: {len(valid_notes)}/{len(notes)} notes valid")
        return valid_notes

    @staticmethod
    def validate_context_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate retrieved context documents.

        Args:
            documents: List of retrieved documents

        Returns:
            Validated list of documents

        Raises:
            ValidationError: Documents contain invalid data
        """
        if not documents:
            logger.warning("No context documents to validate")
            return documents

        valid_docs = []
        for doc in documents:
            try:
                # Check required fields
                if "content" not in doc:
                    logger.warning("Document missing 'content' field")
                    continue

                if "note_path" not in doc:
                    logger.warning("Document missing 'note_path' field")
                    continue

                # Validate content is not empty
                if not doc["content"].strip():
                    logger.warning(f"Document from {doc['note_path']} has empty content")
                    continue

                # Validate similarity score if present
                if "similarity_score" in doc:
                    score = doc["similarity_score"]
                    if not isinstance(score, (int, float)) or score < 0 or score > 1:
                        logger.warning(f"Invalid similarity score: {score}")
                        continue

                valid_docs.append(doc)

            except Exception as e:
                logger.error(f"Error validating document: {e}")
                continue

        logger.info(f"Context validation passed: {len(valid_docs)}/{len(documents)} docs valid")
        return valid_docs

    @staticmethod
    def validate_session(session: ConversationSession) -> ConversationSession:
        """Validate conversation session before saving.

        Args:
            session: Conversation session to validate

        Returns:
            Validated session

        Raises:
            ValidationError: Session contains invalid data
        """
        if not session:
            raise ValidationError("会话不能为空")

        if not session.user_query or not session.user_query.strip():
            raise ValidationError("会话的用户查询不能为空")

        if not session.created_at:
            raise ValidationError("会话必须包含创建时间")

        # Validate agent responses if present
        if hasattr(session, "agent_responses") and session.agent_responses:
            for response in session.agent_responses:
                if not response.response_text or not response.response_text.strip():
                    logger.warning(f"Agent response empty for session {session.session_id}")
                    # Don't fail validation, just warn

        logger.info(f"Session validation passed: {session.session_id}")
        return session

    @staticmethod
    def validate_directory_path(directory_path: str) -> str:
        """Validate directory path for notes.

        Args:
            directory_path: Path to directory

        Returns:
            Validated directory path

        Raises:
            ValidationError: Directory path is invalid
        """
        if not directory_path or not directory_path.strip():
            raise ValidationError("目录路径不能为空")

        path = Path(directory_path)

        if not path.exists():
            raise ValidationError(f"目录不存在: {directory_path}")

        if not path.is_dir():
            raise ValidationError(f"路径不是目录: {directory_path}")

        if not os.access(path, os.R_OK):
            raise ValidationError(f"目录不可读: {directory_path}")

        # Check for markdown files
        md_files = list(path.glob("*.md"))
        if not md_files:
            logger.warning(f"No .md files found in directory: {directory_path}")

        logger.info(f"Directory validation passed: {directory_path}")
        return str(path.absolute())

    @staticmethod
    def validate_vector_store_state(vector_store) -> bool:
        """Validate vector store state before search.

        Args:
            vector_store: VectorStore instance

        Returns:
            True if valid

        Raises:
            ValidationError: Vector store is in invalid state
        """
        if not vector_store:
            raise ValidationError("向量存储未初始化")

        if not hasattr(vector_store, "client") or not vector_store.client:
            raise ValidationError("向量存储客户端未初始化")

        # Check if collection exists
        if hasattr(vector_store, "collection"):
            if not vector_store.collection:
                logger.warning("Vector store collection is empty")
                return True  # Not an error, just empty

        logger.info("Vector store validation passed")
        return True

    @staticmethod
    def validate_llm_response(response: str, agent_type: str) -> str:
        """Validate LLM response before returning to user.

        Args:
            response: LLM response text
            agent_type: Type of agent

        Returns:
            Validated response

        Raises:
            ValidationError: Response is invalid
        """
        if not response or not response.strip():
            raise ValidationError(f"{agent_type} 响应为空")

        if len(response) < 10:
            logger.warning(f"{agent_type} response very short: {response}")

        # Check for error indicators in response
        error_indicators = ["error", "exception", "traceback", "failed"]
        response_lower = response.lower()
        if any(indicator in response_lower for indicator in error_indicators):
            logger.warning(f"{agent_type} response contains error indicators")

        logger.info(f"{agent_type} response validation passed")
        return response.strip()


# Decorator for automatic validation
def validate_input(validation_func):
    """Decorator to validate function inputs.

    Args:
        validation_func: Validation function to apply
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Apply validation to first argument if it's a string
            if args and isinstance(args[0], str):
                args = (validation_func(args[0]),) + args[1:]
            return func(*args, **kwargs)
        return wrapper
    return decorator
