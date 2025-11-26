"""Performance monitoring and metrics for Echo-Board application."""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

from .logging import EchoBoardLogger

logger = EchoBoardLogger.get_logger("performance")


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single session."""

    session_id: str
    start_time: float
    end_time: Optional[float] = None
    total_time: Optional[float] = None

    # Agent timings
    agent_timings: Dict[str, float] = field(default_factory=dict)

    # Component timings
    retrieval_time: Optional[float] = None
    processing_time: Optional[float] = None
    database_time: Optional[float] = None

    # Metadata
    query: str = ""
    num_context_docs: int = 0
    errors: List[str] = field(default_factory=list)

    def complete(self) -> None:
        """Mark session as complete and calculate total time."""
        self.end_time = time.time()
        self.total_time = self.end_time - self.start_time

    def add_agent_time(self, agent_type: str, timing: float) -> None:
        """Add agent processing time."""
        self.agent_timings[agent_type] = timing

    def add_error(self, error: str) -> None:
        """Add an error to the metrics."""
        self.errors.append(error)

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary."""
        return {
            "session_id": self.session_id,
            "query": self.query,
            "total_time": self.total_time,
            "agent_timings": self.agent_timings,
            "retrieval_time": self.retrieval_time,
            "processing_time": self.processing_time,
            "database_time": self.database_time,
            "num_context_docs": self.num_context_docs,
            "errors": self.errors,
        }


class PerformanceMonitor:
    """Monitor performance across the application."""

    def __init__(self):
        """Initialize performance monitor."""
        self.current_metrics: Dict[str, PerformanceMetrics] = {}
        self.completed_sessions: List[PerformanceMetrics] = []

    def start_session(self, session_id: str, query: str) -> PerformanceMetrics:
        """Start monitoring a new session.

        Args:
            session_id: Unique session identifier
            query: User query string

        Returns:
            PerformanceMetrics object for this session
        """
        metrics = PerformanceMetrics(
            session_id=session_id,
            start_time=time.time(),
            query=query,
        )
        self.current_metrics[session_id] = metrics

        logger.info(f"Started performance monitoring for session {session_id}")
        return metrics

    def end_session(self, session_id: str) -> Optional[PerformanceMetrics]:
        """End monitoring for a session.

        Args:
            session_id: Session ID to complete

        Returns:
            Completed PerformanceMetrics object or None if not found
        """
        if session_id not in self.current_metrics:
            logger.warning(f"No metrics found for session {session_id}")
            return None

        metrics = self.current_metrics[session_id]
        metrics.complete()

        # Log performance summary
        logger.info(
            f"Session {session_id} completed in {metrics.total_time:.2f}s. "
            f"Agents: {metrics.agent_timings}"
        )

        # Move to completed sessions
        self.completed_sessions.append(metrics)
        del self.current_metrics[session_id]

        return metrics

    def record_agent_time(self, session_id: str, agent_type: str, timing: float) -> None:
        """Record agent processing time.

        Args:
            session_id: Session identifier
            agent_type: Type of agent (archivist, strategist, coach)
            timing: Processing time in seconds
        """
        if session_id in self.current_metrics:
            self.current_metrics[session_id].add_agent_time(agent_type, timing)
            logger.debug(f"Agent {agent_type} took {timing:.2f}s for session {session_id}")

    def record_retrieval_time(self, session_id: str, timing: float, num_docs: int) -> None:
        """Record vector search retrieval time.

        Args:
            session_id: Session identifier
            timing: Retrieval time in seconds
            num_docs: Number of documents retrieved
        """
        if session_id in self.current_metrics:
            metrics = self.current_metrics[session_id]
            metrics.retrieval_time = timing
            metrics.num_context_docs = num_docs
            logger.debug(f"Retrieval took {timing:.2f}s, found {num_docs} docs for session {session_id}")

    def record_database_time(self, session_id: str, timing: float) -> None:
        """Record database operation time.

        Args:
            session_id: Session identifier
            timing: Database operation time in seconds
        """
        if session_id in self.current_metrics:
            self.current_metrics[session_id].database_time = timing
            logger.debug(f"Database operation took {timing:.2f}s for session {session_id}")

    def record_error(self, session_id: str, error: str) -> None:
        """Record an error for a session.

        Args:
            session_id: Session identifier
            error: Error message
        """
        if session_id in self.current_metrics:
            self.current_metrics[session_id].add_error(error)
            logger.error(f"Error in session {session_id}: {error}")

    def get_session_metrics(self, session_id: str) -> Optional[PerformanceMetrics]:
        """Get metrics for a specific session.

        Args:
            session_id: Session identifier

        Returns:
            PerformanceMetrics object or None if not found
        """
        # Check current sessions
        if session_id in self.current_metrics:
            return self.current_metrics[session_id]

        # Check completed sessions
        for metrics in self.completed_sessions:
            if metrics.session_id == session_id:
                return metrics

        return None

    def get_average_metrics(self, limit: int = 100) -> Dict[str, float]:
        """Get average metrics across completed sessions.

        Args:
            limit: Number of recent sessions to consider

        Returns:
            Dictionary with average metrics
        """
        if not self.completed_sessions:
            return {}

        recent_sessions = self.completed_sessions[-limit:]

        avg_total = sum(m.total_time or 0 for m in recent_sessions) / len(recent_sessions)
        avg_retrieval = sum(m.retrieval_time or 0 for m in recent_sessions) / len(recent_sessions)
        avg_processing = sum(m.processing_time or 0 for m in recent_sessions) / len(recent_sessions)

        # Average agent times
        agent_averages = {}
        for agent_type in ["archivist", "strategist", "coach"]:
            times = [m.agent_timings.get(agent_type, 0) for m in recent_sessions]
            if times:
                agent_averages[agent_type] = sum(times) / len(times)

        return {
            "average_total_time": avg_total,
            "average_retrieval_time": avg_retrieval,
            "average_processing_time": avg_processing,
            "average_agent_times": agent_averages,
            "total_sessions": len(recent_sessions),
        }

    def get_slow_sessions(self, threshold: float = 10.0) -> List[PerformanceMetrics]:
        """Get sessions that took longer than threshold.

        Args:
            threshold: Time threshold in seconds

        Returns:
            List of slow sessions
        """
        slow_sessions = []
        for metrics in self.completed_sessions:
            if (metrics.total_time or 0) > threshold:
                slow_sessions.append(metrics)

        return slow_sessions

    def export_metrics(self, file_path: Optional[str] = None) -> str:
        """Export all metrics to a JSON file.

        Args:
            file_path: Optional file path. If None, uses default.

        Returns:
            Path to exported file
        """
        if file_path is None:
            file_path = Path("logs") / "performance_metrics.json"

        import json

        metrics_data = {
            "completed_sessions": [m.to_dict() for m in self.completed_sessions],
            "summary": self.get_average_metrics(),
        }

        with open(file_path, "w") as f:
            json.dump(metrics_data, f, indent=2)

        logger.info(f"Exported {len(self.completed_sessions)} sessions to {file_path}")
        return str(file_path)


# Global performance monitor instance
monitor = PerformanceMonitor()


# Context manager for easy performance tracking
class track_time:
    """Context manager to track execution time."""

    def __init__(self, monitor_instance: PerformanceMonitor, operation: str, session_id: Optional[str] = None):
        """Initialize tracking context.

        Args:
            monitor_instance: PerformanceMonitor instance
            operation: Operation name (e.g., 'agent_archivist')
            session_id: Optional session ID
        """
        self.monitor = monitor_instance
        self.operation = operation
        self.session_id = session_id
        self.start_time = None

    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and record."""
        if self.start_time:
            duration = time.time() - self.start_time

            if self.session_id:
                # Parse operation to determine type
                if self.operation.startswith("agent_"):
                    agent_type = self.operation.replace("agent_", "")
                    self.monitor.record_agent_time(self.session_id, agent_type, duration)
                elif self.operation == "retrieval":
                    # This would need num_docs passed separately
                    pass
                elif self.operation == "database":
                    self.monitor.record_database_time(self.session_id, duration)

            logger.debug(f"Operation '{self.operation}' took {duration:.2f}s")
